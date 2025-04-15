from django.shortcuts import render, HttpResponse
from .forms import SignUpForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


# Create your views here.
def signup_page(request):
    form = SignUpForm()
    print("Rendering signup page")  # Debug
    return render(request, 'accounts/signup_page.html', {'form': form})

def login_page(request):
    """
    Render the login page.
    """
    print("Rendering login page")  # Debug
    return render(request, 'accounts/login_page.html')

def signup_user(request):
    print("Signup view called")  # Debug
    if request.method == 'POST':
        print("POST request received")  # Debug
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug
            user = form.save()
            print(f"User {user.username} saved with ID {user.id}")  # Debug
            login(request, user)
            return JsonResponse({'success': True, 'redirect': reverse('medminder:dashboard')})  # Return JSON on success
        else:
            print("Form invalid:", form.errors)  # Debug
            return JsonResponse({'success': False, 'errors': form.errors})  # Return JSON on error
    else:
        print("GET request to signup, redirecting")  # Debug
        return redirect('core:home')  # Redirect to the landing page if not a POST request
    
def login_user(request):
    """
    Handle user login.
    """
    print("Login view called")  # Debug
    if request.method == 'POST':
        print("POST request received")  # Debug
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username'] # Using username as email.
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                print(f"User {user.username} authenticated")
                login(request, user)
                return JsonResponse({'success': True, 'redirect': reverse('medminder:dashboard')})  # Return JSON on success
            else:
                # Authentication failed
                print("Authentication failed")
                return JsonResponse({'success': False, 'errors': {'non_field_errors': ['Invalid username or password.']}}) # Return specific error
        else:
            # Form is invalid
            print("Form invalid:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        print("GET request to login, rendering login page")  # Debug
        form = LoginForm()
        return render(request, 'login_page.html', {'form': form})
    
def logout_view(request):
    # Log the user out.
    logout(request)
    # Redirect to a landing page or login page after logout.
    return redirect(reverse('signup_page'))
    
# def redirect_to_core(request):
#     """
#     Redirect to the core page.
#     """
#     print("Redirecting to core")  # Debug
#     return redirect(reverse('core'))