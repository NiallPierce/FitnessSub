/* jshint esversion: 8, module: true */
/* global Stripe */
"use strict";

// Checkout form handling
export function validateShippingForm() {
    const form = document.getElementById('payment-form');
    if (!form) return false;

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
    const selectedShipping = document.querySelector('input[name="shipping_method"]:checked');
    if (selectedShipping) {
        console.log(`Shipping method changed to: ${selectedShipping.value}`);
        // Here you could add logic to recalculate totals based on shipping
    }
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
    const shippingMethodInputs = document.querySelectorAll('input[name="shipping_method"]');
    shippingMethodInputs.forEach(input => {
        input.addEventListener('change', updateOrderTotal);
    });

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateShippingForm()) {
            console.warn('Form validation failed.');
            return;
        }

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
                console.log('Payment successful');
                // You could redirect or show a success message here
            } else {
                console.error('Payment failed:', result.message);
            }
        } catch (error) {
            console.error('Payment failed:', error);
        }
    });
});
