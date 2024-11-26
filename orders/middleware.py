from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to check if the user is authenticated based on the session.
    Redirects to the login page if the user is not authenticated.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip the login and signup views
        allowed_paths = ['login_view', 'signup_view', 'admin', '']  # Add  allowed paths here
        if request.path.strip('/').split('/')[0] in allowed_paths:
            return None

        # Check if user is logged in
        if not request.session.get('username'):
            return redirect('login_view')  # Redirect to login page if not logged in

        # Proceed with the view
        return None
