import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger('request_logger')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Get user information
        user = request.user if request.user.is_authenticated else "AnonymousUser"
        
        # Log request details before processing
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"{timestamp} - User: {user} - Path: {request.path}")
        
        # Process the request
        response = self.get_response(request)
        
        return response
