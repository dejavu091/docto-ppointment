from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from .forms import ContactInquiryForm, ProductForm, AppointmentForm
from .models import ContactInquiry, PricingPlan, Product, Appointment


def home(request):
    # handle appointment booking from the homepage
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save()
            messages.success(request, 'Your appointment request was received. We will contact you to confirm.')
            admin_emails = [email for _, email in getattr(settings, 'ADMINS', [('Admin', 'admin@example.com')])]
            # send templated notification to admins (plain + html)
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
        'GEOAPIFY_API_KEY': getattr(settings, 'GEOAPIFY_API_KEY', ''),
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
