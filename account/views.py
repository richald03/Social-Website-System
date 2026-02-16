from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile

class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, 'Successfully logged in!')
        return super().form_valid(form)

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def custom_logout(request):
    logout(request)
    return render(request, 'registration/logged_out.html')

@login_required
def edit(request):
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully! Your changes have been saved.')
        else:
            messages.error(request, 'Error updating your profile. Please check the form and try again.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)

    return render(request, 'account/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
