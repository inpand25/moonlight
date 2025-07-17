from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserForm(UserCreationForm):
    phone = forms.CharField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    
    birth_day = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 32)])
    birth_month = forms.ChoiceField(choices=[
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'), ('September', 'September'),
        ('October', 'October'), ('November', 'November'), ('December', 'December')
    ])
    birth_year = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1960, 2026)])

    address = forms.CharField()
    city = forms.CharField()
    district = forms.CharField()
    state = forms.CharField()
    zipcode = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'gender', 'birth_day', 'birth_month', 'birth_year',
                  'address', 'city', 'district', 'state', 'zipcode', 'password1', 'password2']

