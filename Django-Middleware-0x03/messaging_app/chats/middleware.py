# chats/middleware.py
import logging
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

        # Configure logging to file
        handler = logging.FileHandler('requests.log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'AnonymousUser'
        path = request.path
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logger.info(f"{timestamp} - User: {user} - Path: {path}")

        return self.get_response(request)
