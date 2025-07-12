from django import forms

# This function will be called by Allauth only when needed — avoids circular import!
def get_custom_signup_form():
    from allauth.account.forms import SignupForm  # Lazy import here (inside function)

    class CustomSignupForm(SignupForm):
        CUSTOMER_CHOICES = [
            ('Tourist', 'Tourist'),
            ('Guide', 'Guide'),
            ('Translator', 'Translator'),
            ('Operator', 'Operator'),
            ('Moderator', 'Moderator'),
        ]

        type_of_customer = forms.ChoiceField(
            choices=CUSTOMER_CHOICES,
            label="Account Type",
            required=True
        )

        def signup(self, request, user):
            user.type_of_customer = self.cleaned_data['type_of_customer']
            user.save()
            return user

    return CustomSignupForm
