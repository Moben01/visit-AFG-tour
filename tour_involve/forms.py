from django import forms
from .models import Translator

class TranslatorForm(forms.ModelForm):
    class Meta:
        model = Translator
        fields = [
            'name',
            'gender',
            'date_of_birth',
            'phone',
            'email',
            'languages',
            'nationality',
            'experience_years',
            'certifications',
            'bio',
            'available_from',
            'available_to',
            'profile_image',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'available_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'available_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter full name',
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter phone number',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter email address',
        })
        self.fields['languages'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g. English ↔ Pashto, Chinese ↔ Dari',
        })
        self.fields['nationality'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter nationality',
        })
        self.fields['experience_years'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Years of experience',
            'min': 0,
            'type': 'number',
        })
        self.fields['certifications'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter certifications or qualifications',
        })
        self.fields['bio'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Short biography',
        })
        self.fields['profile_image'].widget.attrs.update({
            'class': 'form-control',
        })