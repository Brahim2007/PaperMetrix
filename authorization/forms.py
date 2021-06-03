import django.forms as forms
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from . import models


class Signup(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(Signup,self).__init__(*args,**kwargs)
        self.fields['full_name'].widget.attrs.update({
            'class':'form-control',
            'required':True
        })
        self.fields['email'].widget.attrs.update({
            'class':'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'class':'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'class':'form-control'
        })


    class Meta:
        model = models.User
        fields = ("full_name","email","user_roles","password1","password2")
        widgets = {'user_roles': forms.Select(attrs={'class':'custom-select','required':True})}

class Login(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control'}),required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}),required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data['email']
        try:
            user = models.User.objects.get(email=email)
        except ObjectDoesNotExist:
            error = 'User does not exist'
            field = 'email'
            self.add_error(field,error)
            raise forms.ValidationError(error)

        return self.cleaned_data
