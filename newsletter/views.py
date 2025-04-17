from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm
from .models import NewsletterSubscription

def newsletter_signup(request):
    """ Handle newsletter subscription """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thank you for subscribing to our newsletter!')
                return redirect('home:index')
            except:
                messages.error(request, 'This email is already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    else:
        form = NewsletterForm()

    context = {
        'form': form,
    }
    return render(request, 'newsletter/signup.html', context)