from django.forms import TextInput, EmailInput, PasswordInput, CharField, EmailField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    username = CharField(label='Логин', widget=TextInput(attrs={'placeholder': 'Логин'}))
    email = EmailField(label='Почта', widget=EmailInput(attrs={'placeholder': 'Почта'}))
    password1 = CharField(label='Пароль', widget=PasswordInput(attrs={'placeholder': 'Пароль'}))
    password2 = CharField(label='Повтор пароля', widget=PasswordInput(attrs={'placeholder': 'Повтор пароля'}))

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = CharField(label='Логин', widget=TextInput(attrs={'placeholder': 'Логин'}))
    password = CharField(label='Пароль', widget=PasswordInput(attrs={'placeholder': 'Пароль'}))



