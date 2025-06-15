from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages as django_messages
from django.views.decorators.http import require_POST

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    """
    View to handle user account deletion with confirmation
    """
    # Verify password for security
    if not request.user.check_password(request.POST.get('password', '')):
        django_messages.error(request, 'Incorrect password. Account not deleted.')
        return redirect('user_profile')
    
    # Delete the user account
    user = request.user
    user.delete()
    
    # Logout user after deletion
    from django.contrib.auth import logout
    logout(request)
    
    django_messages.success(request, 'Your account has been permanently deleted.')
    return redirect('home')
