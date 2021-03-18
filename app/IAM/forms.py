from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class IAMUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('email',)


class IAMUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)
