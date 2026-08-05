from django import forms
from .models import Product, ContactInquiry, Appointment, Service


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone', 'department', 'service', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all().order_by('name')
        self.fields['service'].required = False
        self.fields['service'].empty_label = 'Choose a service'


class HospitalRegistrationForm(forms.Form):
    name = forms.CharField(max_length=255, label='Hospital Name')
    address = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows': 2}))
    phone = forms.CharField(max_length=50, required=False, label='Hospital Phone')
    services = forms.CharField(
        max_length=300,
        label='Services',
        help_text='Enter comma-separated service names like Cardiology, Pediatrics',
    )
    doctor_name = forms.CharField(max_length=255, label='Doctor Name')
    doctor_specialty = forms.CharField(max_length=255, required=False, label='Doctor Specialty')
    doctor_phone = forms.CharField(max_length=50, required=False, label='Doctor Phone')
