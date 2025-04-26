from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .forms import NewsletterForm
from .models import NewsletterSubscription
from django.utils import timezone
from datetime import timedelta


def newsletter_signup(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                subscription = form.save(commit=False)
                subscription.is_active = False  # Set to inactive until confirmed
                subscription.save()

                # Generate confirmation token and send email
                token = subscription.generate_confirmation_token()
                confirmation_url = request.build_absolute_uri(
                    reverse('newsletter:confirm_subscription', args=[token])
                )

                # Send confirmation email
                subject = 'Confirm Your Newsletter Subscription'
                message = render_to_string('newsletter/email/newsletter_confirmation.html', {
                    'confirmation_url': confirmation_url,
                })

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [subscription.email],
                    html_message=message,
                    fail_silently=False,
                )

                messages.success(request, 'Please check your email to confirm your subscription.')
                context = {
                    'form': NewsletterForm(),
                    'success': True
                }
                return render(request, 'newsletter/signup.html', context)
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again later.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    else:
        form = NewsletterForm()

    context = {
        'form': form,
    }
    return render(request, 'newsletter/signup.html', context)


def confirm_subscription(request, token):
    """Handle subscription confirmation"""
    try:
        subscription = NewsletterSubscription.objects.get(confirmation_token=token)

        # Check if token is expired (24 hours)
        if subscription.confirmation_sent and \
           timezone.now() - subscription.confirmation_sent > timedelta(hours=24):
            messages.error(request, 'Confirmation link has expired. Please subscribe again.')
            return redirect('newsletter:newsletter_signup')

        # Confirm subscription
        subscription.confirm_subscription()

        # Send welcome email
        profile_url = request.build_absolute_uri(reverse('profiles:profile'))
        subject = 'Welcome to Our Newsletter'
        message = render_to_string('newsletter/email/newsletter_welcome.html', {
            'profile_url': profile_url,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.email],
            html_message=message,
            fail_silently=False,
        )

        messages.success(request, 'Thank you for confirming your subscription!')
        return redirect('home:index')
    except NewsletterSubscription.DoesNotExist:
        messages.error(request, 'Invalid confirmation link.')
        return redirect('newsletter:newsletter_signup')
