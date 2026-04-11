/* ========================================
   Proven — Razorpay Checkout
   ======================================== */

function parseJsonSafely(res) {
    var contentType = res.headers.get('content-type') || '';
    if (contentType.indexOf('application/json') !== -1) {
        return res.json();
    }
    return Promise.resolve({});
}

function redirectToLoginIfNeeded(res) {
    if (res.redirected && res.url && res.url.indexOf('/login') !== -1) {
        window.location.href = '/login?next=' + encodeURIComponent('/pricing');
        return true;
    }
    return false;
}

/**
 * Initialize Razorpay checkout for a subscription plan.
 * @param {string} planId - The plan identifier (e.g., 'starter', 'team')
 */
function initiateCheckout(planId) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    // Create order on server
    fetch('/billing/create-order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ plan_id: planId })
    })
    .then(function (res) {
        if (redirectToLoginIfNeeded(res)) return null;
        return parseJsonSafely(res).then(function (data) {
            if (!res.ok) {
                throw new Error(data.error || data.message || 'Unable to create order. Please try again.');
            }
            return data;
        });
    })
    .then(function (data) {
        if (!data) return;
        if (!data.order_id) {
            alert(data.error || data.message || 'Unable to create order. Please try again.');
            return;
        }

        var options = {
            key: data.key,
            amount: data.amount,
            currency: 'INR',
            name: 'Proven',
            description: 'Proven Subscription',
            order_id: data.order_id,
            handler: function (response) {
                verifyPayment(response, planId);
            },
            prefill: {
                name: data.user_name || '',
                email: data.user_email || ''
            },
            theme: {
                color: '#0f214f'
            },
            modal: {
                ondismiss: function () {
                    // User closed the payment modal
                }
            }
        };

        var rzp = new Razorpay(options);
        rzp.on('payment.failed', function (response) {
            alert('Payment failed: ' + response.error.description);
        });
        rzp.open();
    })
    .catch(function (err) {
        alert(err.message || 'Something went wrong. Please try again.');
    });
}

/**
 * Verify payment with server after Razorpay success.
 */
function verifyPayment(response, planId) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    fetch('/billing/verify-payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_signature: response.razorpay_signature,
            plan_id: planId
        })
    })
    .then(function (res) {
        if (redirectToLoginIfNeeded(res)) return null;
        return parseJsonSafely(res).then(function (data) {
            if (!res.ok) {
                throw new Error(data.error || data.message || 'Payment verification failed.');
            }
            return data;
        });
    })
    .then(function (data) {
        if (!data) return;
        if (data.success) {
            window.location.href = '/settings/billing?upgraded=true';
        } else {
            alert(data.error || data.message || 'Payment verification failed. Please contact support.');
        }
    })
    .catch(function (err) {
        alert(err.message || 'Verification failed. Please contact support if payment was deducted.');
    });
}

function initiateRazorpayPayment(planId) {
    initiateCheckout(planId);
}

window.initiateCheckout = initiateCheckout;
window.initiateRazorpayPayment = initiateRazorpayPayment;

/**
 * Purchase additional contact credits.
 * @param {number} quantity - Number of credits to purchase.
 */
function purchaseCredits(quantity) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    fetch('/billing/purchase-credits', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (!data.order_id) {
            alert(data.message || 'Unable to create order.');
            return;
        }

        var options = {
            key: data.razorpay_key,
            amount: data.amount,
            currency: 'INR',
            name: 'Proven',
            description: quantity + ' Contact Credits',
            order_id: data.order_id,
            handler: function (response) {
                fetch('/billing/verify-credits', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_signature: response.razorpay_signature,
                        quantity: quantity
                    })
                })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert(data.message || 'Credit purchase verification failed.');
                    }
                });
            },
            theme: { color: '#0f214f' }
        };

        var rzp = new Razorpay(options);
        rzp.open();
    })
    .catch(function () {
        alert('Something went wrong. Please try again.');
    });
}
