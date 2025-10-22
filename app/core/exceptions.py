"""
Custom exception classes
"""

class AIFactoryException(Exception):
    """Base exception for AI Social Factory"""
    pass

class VideoGenerationError(AIFactoryException):
    """Video generation failed"""
    pass

class LLMServiceError(AIFactoryException):
    """LLM service error"""
    pass

class SheetsServiceError(AIFactoryException):
    """Google Sheets service error"""
    pass

class SlackServiceError(AIFactoryException):
    """Slack service error"""
    pass

class WordPressServiceError(AIFactoryException):
    """WordPress service error"""
    pass

class LinkedInServiceError(AIFactoryException):
    """LinkedIn service error"""
    pass

class WorkflowError(AIFactoryException):
    """Workflow execution error"""
    pass
