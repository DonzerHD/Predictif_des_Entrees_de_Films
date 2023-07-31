from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = ""
        self.fields['username'].label = "Nom d'utilisateur"
        
        self.fields['password1'].help_text = " "
        self.fields['password1'].label = "Mot de passe"
        
        self.fields['password2'].help_text = ""
        self.fields['password2'].label = "Confirmez votre mot de passe"

        self.fields['username'].error_messages = {
            "required": "Entrez un nom d'utilisateur.",
            'unique': "Nom d'utilisateur déjà pris",
        }
        self.fields['password1'].error_messages = {
            'required': 'Entrez un mot de passe.',
            'password_mismatch': 'Les mots de passe ne correspondent pas.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Confirmez votre mot de passe.',
            'password_mismatch': 'Les mots de passe ne correspondent pas.',
        }

        self.fields['username'].widget.attrs.update({"placeholder": "Nom d'utilisateur"})
        self.fields['password1'].widget.attrs.update({'placeholder': '8 carac min. chiffre lettres'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmez votre mot de passe'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.fields['password2'].error_messages['password_mismatch'],
                code='password_mismatch',
            )
        
        return password2
