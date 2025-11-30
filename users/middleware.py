from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.conf import settings

class RequireRegistrationMiddleware:
    """Redirect anonymous users to registration page on first access.

    Excludes paths: register, login, logout, admin, static and media files.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # compute some safe defaults; reverse may fail at import time in some setups,
        # so wrap reverses in try/except and fallback to literal paths.
        try:
            self.register_path = reverse('register')
        except NoReverseMatch:
            self.register_path = '/users/register/'
        try:
            self.login_path = reverse('login')
        except NoReverseMatch:
            self.login_path = '/users/login/'
        try:
            self.logout_path = reverse('logout')
        except NoReverseMatch:
            self.logout_path = '/users/logout/'
        # admin and media/static
        self.admin_path = '/admin/'
        self.static_url = getattr(settings, 'STATIC_URL', '/static/')
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')

        # paths we always allow for anonymous
        self.allowed_starts = (
            self.register_path,
            self.login_path,
            self.logout_path,
            self.admin_path,
            self.static_url,
            self.media_url,
            '/favicon.ico',
        )

    def __call__(self, request):
        # If user is authenticated, allow
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            return self.get_response(request)

        path = request.path
        # Allow explicitly allowed paths and API metadata (optional)
        for prefix in self.allowed_starts:
            if path.startswith(prefix):
                return self.get_response(request)

        # Also allow Django admin static auto paths (e.g., /admin/login/)
        if path.startswith('/admin/'):
            return self.get_response(request)

        # Otherwise redirect to register page
        return redirect(self.register_path)
