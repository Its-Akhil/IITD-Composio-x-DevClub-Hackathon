"""
LLM service using Google Gemini API
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.config import settings
from app.models import ScriptGenerationRequest, ScriptGenerationResponse, ScriptVariant
from app.models import CaptionRequest, CaptionResponse
from app.core.exceptions import LLMServiceError
from app.utils.json_utils import parse_llm_json, clean_json_response
from pydantic import Field
logger = logging.getLogger(__name__)

class LLMService:
    """Google Gemini API service"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured")
            self.configured = False
            return
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.configured = True
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"LLMService initialized with model: {settings.GEMINI_MODEL}")
    
    async def analyze_trend(self, topic: str) -> Dict[str, Any]:
        """Analyze trending topic and provide insights"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        prompt = f"""Analyze the following topic and provide insights for creating engaging social media content:

Topic: {topic}

Provide:
1. Current trends related to this topic
2. Key angles to explore
3. Target audience interests
4. Recommended content style
5. Hashtag suggestions

Format as JSON."""
        
        try:
            response = await self._generate_content(prompt)
            # Parse JSON response
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise LLMServiceError(f"Trend analysis failed: {str(e)}")
    
    async def generate_script(
        self,
        request: ScriptGenerationRequest
    ) -> ScriptGenerationResponse:
        """Generate multiple script variants (alias for generate_scripts)"""
        return await self.generate_scripts(request)
    
    async def generate_scripts(
        self,
        request: ScriptGenerationRequest
    ) -> ScriptGenerationResponse:
        """Generate multiple script variants using structured output"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        prompt = f"""Generate {request.num_variants} engaging video script variants for social media.

Topic: {request.topic}
Platform: {request.platform}
Target Duration: {request.target_duration} seconds

Requirements:
- Create exactly {request.num_variants} unique and creative scripts
- Each script should have: Hook (first 2 seconds), Main content, and Call-to-Action
- Use platform-appropriate tone for {request.platform}
- Assign variant IDs as single letters ONLY: A, B, C (no numbers, no suffixes)
- Keep scripts concise and engaging (max 500 words each)
- Estimate duration for each script in seconds
- Use different styles: educational, conversational, motivational
"""
        
        # Define Pydantic-like schema for structured output
        from pydantic import BaseModel
        from typing import List
        
        class ScriptVariantSchema(BaseModel):
            variant_id: str = Field(description="Single letter variant identifier: A, B, or C only")
            script: str = Field(description="The generated script text, max 500 words")
            style: str = Field(description="Style: educational, conversational, or motivational")
            duration_estimate: int = Field(description="Estimated duration in seconds")
        
        class ScriptsResponse(BaseModel):
            variants: List[ScriptVariantSchema]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=ScriptsResponse,
                        max_output_tokens=4096,  # Limit response size
                        temperature=0.7
                    )
                )
            )
            
            # Parse JSON response with robust error handling
            logger.info(f"Received response from Gemini (length: {len(response.text)})")
            
            try:
                data = parse_llm_json(response.text)
            except Exception as parse_error:
                logger.error(f"JSON parse error: {parse_error}")
                logger.error(f"Response text (first 500 chars): {response.text[:500]}")
                raise LLMServiceError(
                    f"Failed to parse script generation response. "
                    f"The AI returned invalid JSON format. "
                    f"Error: {str(parse_error)}"
                )
            
            # Validate we have variants
            if 'variants' not in data:
                logger.error(f"Response missing 'variants' key. Keys: {data.keys()}")
                raise LLMServiceError("Invalid response format: missing 'variants'")
            
            # Parse variants with detailed error handling
            variants = []
            for idx, v in enumerate(data['variants']):
                try:
                    # Validate required keys
                    required_keys = ['variant_id', 'script', 'style', 'duration_estimate']
                    missing_keys = [k for k in required_keys if k not in v]
                    if missing_keys:
                        logger.error(f"Variant {idx} missing keys: {missing_keys}. Available keys: {list(v.keys())}")
                        raise LLMServiceError(f"Variant {idx} missing required fields: {', '.join(missing_keys)}")
                    
                    # Clean up variant_id - take only first character if it's malformed
                    variant_id = str(v['variant_id']).strip()
                    if len(variant_id) > 10:  # Definitely malformed
                        logger.warning(f"Variant {idx} has malformed ID (length {len(variant_id)}), using letter {chr(65+idx)}")
                        variant_id = chr(65 + idx)  # A, B, C, etc.
                    elif len(variant_id) > 1:
                        # Take first character
                        variant_id = variant_id[0].upper()
                    
                    variant = ScriptVariant(
                        variant_id=variant_id,
                        script=v['script'],
                        style=v['style'],
                        duration_estimate=int(v['duration_estimate'])
                    )
                    variants.append(variant)
                except KeyError as ke:
                    logger.error(f"KeyError in variant {idx}: {ke}. Variant data: {v}")
                    raise LLMServiceError(f"Missing required field in variant {idx}: {ke}")
                except Exception as ve:
                    logger.error(f"Error parsing variant {idx}: {ve}. Variant data: {v}")
                    raise LLMServiceError(f"Failed to parse variant {idx}: {ve}")
            
            logger.info(f"Successfully generated {len(variants)} script variants")
            
            return ScriptGenerationResponse(
                topic=request.topic,
                variants=variants,
                metadata={"platform": request.platform}
            )
            
        except LLMServiceError:
            raise
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise LLMServiceError(f"Script generation failed: {str(e)}")
    
    async def generate_caption(
        self,
        request: CaptionRequest
    ) -> CaptionResponse:
        """Generate platform-specific caption with hashtags using structured output"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        platform_guidelines = {
            "instagram": "Engaging, visual-focused, 2-3 lines, 5-10 hashtags",
            "youtube": "Detailed, SEO-optimized, clear description, 3-5 hashtags",
            "tiktok": "Short, trendy, relatable, 3-5 trending hashtags",
            "linkedin": "Professional, value-driven, thought leadership, 2-3 hashtags",
            "twitter": "Concise, punchy, under 280 chars, 1-2 hashtags",
            "wordpress": "Blog-style, SEO-friendly, detailed, 3-8 relevant hashtags for categorization"
        }
        
        guideline = platform_guidelines.get(request.platform, "General engaging caption")
        max_length_info = f"Max length: {request.max_length} chars" if request.max_length else ""
        
        prompt = f"""Create an engaging caption for {request.platform}.

Video Script: {request.script}
Style Guidelines: {guideline}
{max_length_info}
Include Hashtags: {request.include_hashtags}

Generate a compelling caption that matches the platform's style and engages the audience.
"""
        
        # Define Pydantic schema for structured output
        from pydantic import BaseModel
        from typing import List
        
        class CaptionSchema(BaseModel):
            caption: str
            hashtags: List[str]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=CaptionSchema
                    )
                )
            )
            
            # Parse JSON response with robust error handling
            logger.info(f"Received caption response from Gemini (length: {len(response.text)})")
            
            try:
                data = parse_llm_json(response.text)
            except Exception as parse_error:
                logger.error(f"JSON parse error: {parse_error}")
                logger.error(f"Response text (first 500 chars): {response.text[:500]}")
                raise LLMServiceError(
                    f"Failed to parse caption generation response. "
                    f"The AI returned invalid JSON format. "
                    f"Error: {str(parse_error)}"
                )
            
            caption = str(data.get('caption', ''))
            hashtags = list(data.get('hashtags', [])) if request.include_hashtags else []
            
            return CaptionResponse(
                caption=caption,
                hashtags=hashtags,
                platform=request.platform,
                character_count=len(caption)
            )
            
        except LLMServiceError:
            raise
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            raise LLMServiceError(f"Caption generation failed: {str(e)}")
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise LLMServiceError(f"API call failed: {str(e)}")
    
    async def _generate_content_structured(self, prompt: str, response_schema: Dict[str, Any]) -> Any:
        """Generate structured content using Gemini API with response schema"""
        try:
            import json
            import re
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_structured_sync,
                prompt,
                response_schema
            )
            
            # Clean the response text
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*\n?', '', text)
                text = re.sub(r'\n?```\s*$', '', text)
                text = text.strip()
            
            # Try to extract just the JSON part if there's extra text
            # Look for JSON array or object
            json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
            if json_match:
                text = json_match.group(1)
            
            # Parse the JSON response
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nResponse text: {response.text[:500]}")
            raise LLMServiceError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise LLMServiceError(f"API call failed: {str(e)}")
    
    def _generate_sync(self, prompt: str):
        """Synchronous generation (runs in thread pool)"""
        generation_config = {
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }
        return self.model.generate_content(prompt, generation_config=generation_config)
    
    def _generate_structured_sync(self, prompt: str, response_schema: Dict[str, Any]):
        """Synchronous structured generation with response schema (runs in thread pool)"""
        # Add schema to prompt for better JSON generation
        schema_prompt = f"""{prompt}

CRITICAL: Respond ONLY with valid JSON matching this exact schema:
{response_schema}

Do not include any markdown, explanations, or text outside the JSON object."""
        
        generation_config = {
            "temperature": 0.7,  # Lower temperature for more consistent JSON
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }
        return self.model.generate_content(schema_prompt, generation_config=generation_config)


