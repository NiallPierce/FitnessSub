// Checkout form handling
export function validateShippingForm() {
    const form = document.getElementById('payment-form');
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

export function showSection(sectionIndex) {
    const sections = document.querySelectorAll('.checkout-section');
    sections.forEach((section, index) => {
        if (index === sectionIndex) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
}

export function updateOrderTotal() {
    const shippingMethod = document.querySelector('input[name="shipping_method"]:checked').value;
    // In a real implementation, this would calculate and update the total
    console.log(`Shipping method changed to: ${shippingMethod}`);
}

export async function initializePaymentElement() {
    const stripe = Stripe('your_publishable_key');
    const elements = stripe.elements();
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payment-form');
    if (!form) {
        return;
    }

    // Shipping method change handler
    const shippingMethodInput = document.querySelector('input[name="shipping_method"]');
    if (shippingMethodInput) {
        shippingMethodInput.addEventListener('change', updateOrderTotal);
    }

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await initializePaymentElement();

        try {
            const response = await fetch('/checkout/process/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            const result = await response.json();
            if (result.success) {
                // Handle successful payment
                console.log('Payment successful');
            }
        } catch (error) {
            console.error('Payment failed:', error);
        }
    });
});
