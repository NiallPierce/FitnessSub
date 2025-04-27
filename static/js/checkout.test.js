// Import the actual implementation
import { validateShippingForm, showSection, updateOrderTotal, initializePaymentElement } from './checkout.js';

// Mock Stripe for testing
const mockStripe = {
    elements: jest.fn().mockReturnValue({
        create: jest.fn().mockReturnValue({
            mount: jest.fn()
        })
    }),
    confirmPayment: jest.fn()
};

// Mock global Stripe object
global.Stripe = jest.fn().mockReturnValue(mockStripe);

// Mock fetch
global.fetch = jest.fn();

describe('Checkout Form', () => {
    beforeEach(() => {
        // Reset mocks before each test
        jest.clearAllMocks();

        // Set up the DOM
        document.body.innerHTML = `
            <form id="payment-form">
                <div class="checkout-section active" id="shipping-section">
                    <input name="first_name" value="John" required>
                    <input name="last_name" value="Doe" required>
                    <input name="email" value="john@example.com" required>
                    <input name="address" value="123 Main St" required>
                    <input name="postal_code" value="12345" required>
                    <input name="city" value="New York" required>
                    <input name="country" value="USA" required>
                    <input type="radio" name="shipping_method" value="standard" checked>
                </div>
                <div class="checkout-section" id="payment-section">
                    <div id="payment-element"></div>
                </div>
                <div class="checkout-section" id="review-section">
                    <div id="review-shipping-info"></div>
                    <div id="review-shipping-method"></div>
                </div>
                <button type="button" id="next-to-payment">Continue to Payment</button>
                <button type="button" id="back-to-shipping">Back to Shipping</button>
                <button type="button" id="next-to-review">Continue to Review</button>
                <button type="button" id="back-to-payment">Back to Payment</button>
                <button type="submit" id="submit-button">
                    <span id="button-text">Place Order</span>
                    <span id="spinner" class="d-none"></span>
                </button>
            </form>
        `;

        // Set up event listeners
        document.getElementById('next-to-payment').addEventListener('click', async () => {
            if (validateShippingForm()) {
                showSection(1);
                await initializePaymentElement();
            }
        });

        document.getElementById('back-to-shipping').addEventListener('click', () => {
            showSection(0);
        });

        const shippingMethodInput = document.querySelector('input[name="shipping_method"]');
        shippingMethodInput.addEventListener('change', updateOrderTotal);

        document.getElementById('payment-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await initializePaymentElement();
            await global.fetch('/checkout/process/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            await mockStripe.confirmPayment();
        });
    });

    describe('Form Validation', () => {
        test('validates required fields', () => {
            // Test with valid data
            expect(validateShippingForm()).toBe(true);

            // Test with invalid data
            document.querySelector('[name="first_name"]').value = '';
            expect(validateShippingForm()).toBe(false);
            expect(document.querySelector('[name="first_name"]').classList.contains('is-invalid')).toBe(true);
        });

        test('validates email format', () => {
            const emailInput = document.querySelector('[name="email"]');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            // Test valid email
            emailInput.value = 'test@example.com';
            expect(emailRegex.test(emailInput.value)).toBe(true);

            // Test invalid email
            emailInput.value = 'invalid-email';
            expect(emailRegex.test(emailInput.value)).toBe(false);
        });
    });

    describe('Step Navigation', () => {
        test('shows correct section when navigating', async () => {
            // Test navigation to payment section
            document.getElementById('next-to-payment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(document.getElementById('payment-section').classList.contains('active')).toBe(true);
            expect(document.getElementById('shipping-section').classList.contains('active')).toBe(false);

            // Test navigation back to shipping
            document.getElementById('back-to-shipping').click();
            expect(document.getElementById('shipping-section').classList.contains('active')).toBe(true);
            expect(document.getElementById('payment-section').classList.contains('active')).toBe(false);
        });
    });

    describe('Shipping Cost Calculation', () => {
        test('calculates shipping costs correctly', () => {
            const consoleSpy = jest.spyOn(console, 'log');
            const standardShipping = document.querySelector('input[value="standard"]');
            standardShipping.checked = true;
            standardShipping.dispatchEvent(new Event('change'));
            expect(consoleSpy).toHaveBeenCalledWith('Shipping method changed to: standard');
            consoleSpy.mockRestore();
        });
    });

    describe('Stripe Integration', () => {
        test('initializes Stripe correctly', async () => {
            // Click the next button
            document.getElementById('next-to-payment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.Stripe).toHaveBeenCalledWith('your_publishable_key');
            expect(mockStripe.elements).toHaveBeenCalled();
        });

        test('handles payment submission', async () => {
            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({
                    success: true,
                    order_id: 'test_order_123'
                })
            });

            // Mock successful Stripe confirmation
            mockStripe.confirmPayment.mockResolvedValueOnce({ error: null });

            // Submit the form
            document.getElementById('payment-form').dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith('/checkout/process/', expect.any(Object));
            expect(mockStripe.confirmPayment).toHaveBeenCalled();
        });
    });
});
