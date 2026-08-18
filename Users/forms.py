from django import forms
from django.contrib.auth import get_user_model
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class registerForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username','email','password','avatar','first_name','last_name','id_country']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise ValidationError('Tên người dùng đã sử dụng')
        return username
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('email đã sử dụng')
        return email
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if avatar:
            if avatar.size > 1024 * 1024:
                raise ValidationError('Ảnh không được quá 1MB')
            if not avatar.name.lower().endswith(('.png','.jpeg','.jpg')):
                raise ValidationError('Chỉ chấp nhận ảnh jpg,jpeg,png')
        return avatar
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        confirm_pw = cleaned_data.get('confirm_password')
        if pw and confirm_pw and confirm_pw != pw:
            raise ValidationError('Mật khẩu không khớp')
        return cleaned_data

class loginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'username'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'password'
            }
        )
    )