from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from .forms import ContactInquiryForm, ProductForm, AppointmentForm, HospitalRegistrationForm
from .models import ContactInquiry, PricingPlan, Product, Appointment, Service, Hospital, Doctor


def home(request):
    appointment_match = request.session.pop('appointment_match_info', None)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            service = appt.service
            department = appt.department or ''

            hospitals = Hospital.objects.filter(is_active=True)
            if service:
                hospitals = hospitals.filter(services=service)

            available_doctors = Doctor.objects.filter(is_available=True, hospital__in=hospitals)
            if department:
                available_doctors = available_doctors.filter(specialty__icontains=department)

            selected_doctor = available_doctors.order_by('hospital__name', 'name').first()
            selected_hospital = selected_doctor.hospital if selected_doctor else hospitals.order_by('name').first()

            if selected_hospital:
                appt.hospital = selected_hospital
            if selected_doctor:
                appt.doctor = selected_doctor
            appt.save()

            request.session['appointment_match_info'] = {
                'service': appt.service.name if appt.service else appt.department,
                'hospital': appt.hospital.name if appt.hospital else 'No hospital matched',
                'doctor': appt.doctor.name if appt.doctor else '',
            }

            messages.success(request, 'Your appointment request was received. We will contact you to confirm.')
            admin_emails = [email for _, email in getattr(settings, 'ADMINS', [('Admin', 'admin@example.com')])]
            subject = f'New appointment request: {appt.name}'
            txt = render_to_string('appointment/emails/appointment_notification.txt', {'appt': appt})
            html = render_to_string('appointment/emails/appointment_notification.html', {'appt': appt})
            send_mail(
                subject,
                txt,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@docto-ppointment.local'),
                admin_emails,
                fail_silently=True,
                html_message=html,
            )
            return redirect('home')
    else:
        form = AppointmentForm()

    return render(request, 'appointment/homepage.html', {
        'appointment_form': form,
        'appointment_match': appointment_match,
        'GEOAPIFY_API_KEY': getattr(settings, 'GEOAPIFY_API_KEY', ''),
        'services': Service.objects.all().order_by('name'),
        'hospitals': Hospital.objects.filter(is_active=True).order_by('name'),
    })


def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            hospital_name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']
            services_raw = form.cleaned_data['services']
            doctor_name = form.cleaned_data['doctor_name']
            doctor_specialty = form.cleaned_data['doctor_specialty']
            doctor_phone = form.cleaned_data['doctor_phone']

            hospital, _ = Hospital.objects.get_or_create(name=hospital_name, defaults={
                'address': address,
                'phone': phone,
                'is_active': True,
            })
            if hospital.address != address:
                hospital.address = address
            if hospital.phone != phone:
                hospital.phone = phone
            hospital.is_active = True
            hospital.save()

            service_names = [name.strip() for name in services_raw.split(',') if name.strip()]
            for name in service_names:
                service, _ = Service.objects.get_or_create(name=name)
                hospital.services.add(service)

            Doctor.objects.get_or_create(
                name=doctor_name,
                hospital=hospital,
                defaults={
                    'specialty': doctor_specialty,
                    'phone': doctor_phone,
                    'is_available': True,
                }
            )
            messages.success(request, 'Hospital and doctor registered successfully. Patients can now book by service.')
            return redirect('register_hospital')
    else:
        form = HospitalRegistrationForm()

    return render(request, 'appointment/hospital_register.html', {
        'register_form': form,
    })


def products(request):
    is_superuser = request.user.is_authenticated and request.user.is_superuser

    if request.method == 'POST':
        if not is_superuser:
            return redirect('products')
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm() if is_superuser else None

    products = Product.objects.all().order_by('-created_at')
    return render(request, 'appointment/products.html', {
        'products': products,
        'form': form,
        'can_upload': is_superuser,
    })


def pricing(request):
    plans = PricingPlan.objects.all()
    if not plans.exists():
        PricingPlan.objects.bulk_create([
            PricingPlan(name='Basic Health Check', description='Basic consultation and tests', price=199.99),
            PricingPlan(name='Standard Care', description='Consultation, follow-up, and medication', price=399.99),
            PricingPlan(name='Premium Care', description='Full service with priority booking and specialist review', price=699.99),
        ])
        plans = PricingPlan.objects.all()

    return render(request, 'appointment/pricing.html', {
        'plans': plans,
    })


def checkout_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        messages.success(request, f'Purchase confirmed for "{product.name}". We will contact you soon.')
        return redirect('products')
    return render(request, 'appointment/checkout.html', {
        'item': product,
        'item_type': 'product',
        'back_url': 'products',
        'action_label': 'Confirm Purchase',
        'title': 'Buy Product',
    })


def checkout_plan(request, plan_id):
    plan = get_object_or_404(PricingPlan, pk=plan_id)
    if request.method == 'POST':
        messages.success(request, f'Subscription confirmed for "{plan.name}". We will contact you soon.')
        return redirect('pricing')
    return render(request, 'appointment/checkout.html', {
        'item': plan,
        'item_type': 'plan',
        'back_url': 'pricing',
        'action_label': 'Confirm Subscription',
        'title': 'Subscribe to Plan',
    })


def contact(request):
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, 'Your message has been sent. The admin will review it shortly.')
            admin_emails = [email for _, email in getattr(settings, 'ADMINS', [('Admin', 'admin@example.com')])]
            # send templated notification to admins (plain + html)
            subject = f'New contact inquiry: {inquiry.subject}'
            txt = render_to_string('appointment/emails/contact_notification.txt', {'inquiry': inquiry})
            html = render_to_string('appointment/emails/contact_notification.html', {'inquiry': inquiry})
            send_mail(
                subject,
                txt,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@docto-ppointment.local'),
                admin_emails,
                fail_silently=True,
                html_message=html,
            )
            return redirect('contact')
    else:
        form = ContactInquiryForm()

    can_see_inquiries = request.user.is_authenticated and request.user.is_superuser
    inquiries = ContactInquiry.objects.order_by('-created_at') if can_see_inquiries else None
    return render(request, 'appointment/contact.html', {
        'form': form,
        'inquiries': inquiries,
        'can_see_inquiries': can_see_inquiries,
    })


def about(request):
    return render(request, 'appointment/about.html')


def custom_404(request, exception=None):
    return render(request, 'appointment/404.html', status=404)


def custom_500(request):
    return render(request, 'appointment/500.html', status=500)
