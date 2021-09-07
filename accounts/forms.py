from django import forms
from django.contrib.auth import password_validation
from user_management.models import User


class LogInForm(forms.Form):
    """Login Form."""

    email = forms.EmailField(label='Email', error_messages={'required': "Enter email address"}, widget=forms.EmailInput(
        attrs={'placeholder': 'Email Address'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(render_value=True, attrs={'placeholder': 'Password'}),
                               error_messages={'required': "Enter password"})


class UserProfileForm(forms.ModelForm):
    """
    User profile form.
    """

    class Meta:
        model = User
        fields = "__all__"


class ProfileUpdateForm(forms.ModelForm):
    """
    User profile form.
    """

    class Meta:
        model = User
        fields = '__all__'


class UserProfileUpdateForm(forms.ModelForm):
    """
    User profile form.
    """

    class Meta:
        model = User
        fields = '__all__'


class ChangeProfilePictureForm(forms.ModelForm):
    """
    Update profile picture form.
    """

    profile_picture = forms.ImageField(label='Select Profile Picture', required=True)

    class Meta:
        model = User
        fields = ('profile_picture',)


class UpdateUserPasswordForm(forms.ModelForm):
    """
    Update password form.
    """

    password = forms.CharField(label='Old Password', widget=forms.PasswordInput(render_value=True,
                                                                                attrs={'placeholder': 'Password'}),
                               error_messages={'required': "The password field is required."})
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(render_value=True,
                                                                                    attrs={
                                                                                        'placeholder': 'New Password'}),
                                   error_messages={'required': "The password field is required."})
    password_confirmation = forms.CharField(label='Confirm New Password',
                                            widget=forms.PasswordInput(render_value=True,
                                                                       attrs={'placeholder': 'Confirm Password'}),
                                            error_messages={'required': "The password confirmation field is required."})

    class Meta:
        model = User
        fields = ('password',)

    def clean(self):
        cleaned_data = super(UpdateUserPasswordForm, self).clean()
        new_password = cleaned_data.get('new_password')
        password_confirmation = cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.fields['new_password'].widget = forms.PasswordInput()
            self.fields['password_confirmation'].widget = forms.PasswordInput()
            self.add_error('password_confirmation', 'New Password and Password confirmation do not match')


class UserSearchListForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=False)
    work_phone = forms.CharField(max_length=20, required=False)
    personal_phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=20, required=False)
    state = forms.CharField(max_length=20, required=False)
    rfid = forms.CharField(max_length=20, required=False)
    zip_code = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = '__all__'


class UserChangePasswordForm(forms.Form):
    """
    Form with custom logic to change a user's password (by an admin).
    Please see the django.contrib.auth.forms.AdminPasswordChangeForm class,
    from which this Form has been adapted.
    """
    password1 = forms.CharField(
        label='New password',
        error_messages={'required': 'Please enter a new password'},
        widget=forms.PasswordInput(attrs={'autofocus': True}),
        strip=False,
    )
    password2 = forms.CharField(
        label='Confirm password',
        error_messages={'required': 'Please re-enter the new password'},
        widget=forms.PasswordInput,
        strip=False,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    'The password fields did not match',
                    code='password_mismatch',
                )
            password_validation.validate_password(password1, self.user)
        return self.cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data['password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
