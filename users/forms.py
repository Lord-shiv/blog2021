from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.forms.widgets import DateInput
from .models import Profile, User
from django.contrib import messages
from django.forms.widgets import NumberInput


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        try:
            User.objects.get(username__exact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("This username is already taken.")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(f"Email {email} is already in use.")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('__all__')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RegistrationForm(forms.ModelForm):
    '''NOT using this insted ajax'''
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            User.objects.get(username__exact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("This username is already taken.")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LogInForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError(
                    "Invalid email or password")
        else:
            raise forms.ValidationError("Invlid Input.")


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')


GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)


class UserProfileForm(forms.ModelForm):

    gender = forms.ChoiceField(
        label='Gender', choices=GENDER, widget=forms.RadioSelect, required=False)
    date_of_birth = forms.DateField(widget=NumberInput(
        attrs={'type': 'date'}), required=False)

    # from phonenumber_field.formfields import PhoneNumberField

    # phonenumber = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': _('Phone')}), 

    #                    label=_("Phone number"), required=False)

    # timefield = forms.DateTimeField(input_formats=['%I:%M %p %d-%b-%Y'],
    #                                     widget=forms.DateTimeInput(
    #     attrs={'type': 'datetime-local'},
    #     format='%I:%M %p %d-%b-%Y'), required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'mobile', 'country', 'avatar', 'address', 'gender',
                  'date_of_birth', 'pincode', 'website', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'your last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you emai@gmail.com'}),
            'mobile': forms.NumberInput(attrs={'placeholder': 'your mobile number'}),
            'country': forms.TextInput(attrs={'placeholder': 'country you where you live'}),
            'address': forms.TextInput(attrs={'placeholder': 'your address where you live'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'pincode'}),
            'bio': forms.TextInput(attrs={'placeholder': 'about you'}),
            'website': forms.TextInput(attrs={'placeholder': 'your website url e.g. https://your_website.com'}),
        }
