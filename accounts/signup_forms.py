from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
    ]
    
    my_choice_field = forms.ChoiceField(choices=CHOICES, label="Choose an option")

    def save(self, request):
        user = super().save(request)
        # Save your choice value somewhere, e.g., in user profile or a related model
        # For example, if you have a user profile:
        # user.profile.my_choice_field = self.cleaned_data['my_choice_field']
        # user.profile.save()

        return user
