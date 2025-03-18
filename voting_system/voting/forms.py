from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'role']
class CustomAuthenticationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
# forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(forms.ModelForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES) 

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  
        if commit:
            user.save()
        return user


from django import forms
from .models import VotingTopic, VotingOption

class VotingTopicForm(forms.ModelForm):
    class Meta:
        model = VotingTopic
        fields = ['title', 'description', 'start_time', 'end_time']

class VotingOptionForm(forms.ModelForm):
    class Meta:
        model = VotingOption
        fields = ['option_text']
