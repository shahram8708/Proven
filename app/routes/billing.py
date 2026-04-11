import os
import time
import hmac
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db, csrf

billing_bp = Blueprint('billing', __name__)

PLANS = {
    'employer_starter': {'amount': 829900, 'name': 'Employer Starter', 'display': '₹8,299/month'},
    'employer_team': {'amount': 2919900, 'name': 'Employer Team', 'display': '₹29,199/month'},
    'talent_pro': {'amount': 74900, 'name': 'Talent Pro', 'display': '₹749/month'},
}


def get_razorpay_client():
    import razorpay
    key_id = os.environ.get('RAZORPAY_KEY_ID')
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
    return razorpay.Client(auth=(key_id, key_secret))


@billing_bp.route('/billing/create-order', methods=['POST'])
@login_required
def create_razorpay_order():
    data = request.get_json(silent=True) or {}
    plan_id = data.get('plan_id')
    plan = PLANS.get(plan_id)
    if not plan:
        return jsonify({'error': 'Invalid plan'}), 400

    if plan_id.startswith('employer_') and current_user.account_type != 'employer':
        return jsonify({'error': 'This plan is available for employer accounts only.'}), 403
    if plan_id == 'talent_pro' and current_user.account_type != 'talent':
        return jsonify({'error': 'This plan is available for talent accounts only.'}), 403

    try:
        client = get_razorpay_client()
        order = client.order.create({
            'amount': plan['amount'],
            'currency': 'INR',
            'receipt': f'order_{current_user.id}_{plan_id}_{int(time.time())}',
            'notes': {'user_id': str(current_user.id), 'plan': plan_id},
        })
        return jsonify({
            'order_id': order['id'],
            'amount': plan['amount'],
            'currency': 'INR',
            'key': os.environ.get('RAZORPAY_KEY_ID'),
            'plan_name': plan['name'],
        })
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@billing_bp.route('/billing/verify-payment', methods=['POST'])
@login_required
def verify_razorpay_payment():
    data = request.get_json(silent=True) or {}
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    plan_id = data.get('plan_id')

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'error': 'Missing payment data'}), 400

    if plan_id not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    if plan_id.startswith('employer_') and current_user.account_type != 'employer':
        return jsonify({'error': 'This plan is available for employer accounts only.'}), 403
    if plan_id == 'talent_pro' and current_user.account_type != 'talent':
        return jsonify({'error': 'This plan is available for talent accounts only.'}), 403

    try:
        client = get_razorpay_client()
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })

        current_user.is_premium = True
        current_user.subscription_tier = plan_id
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        current_user.razorpay_customer_id = razorpay_payment_id

        if current_user.employer_account and plan_id in ('employer_starter', 'employer_team'):
            current_user.employer_account.subscription_tier = plan_id.replace('employer_', '')
            if plan_id == 'employer_starter':
                current_user.employer_account.monthly_contact_credits = 10
            elif plan_id == 'employer_team':
                current_user.employer_account.monthly_contact_credits = 50

        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscription activated successfully'})

    except Exception:
        return jsonify({'error': 'Payment verification failed'}), 400


@billing_bp.route('/billing/webhook', methods=['POST'])
@csrf.exempt
def razorpay_webhook():
    webhook_body = request.get_data(as_text=True)
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')
    webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')

    if not webhook_secret:
        return jsonify({'error': 'Webhook secret not configured'}), 500

    generated_signature = hmac.new(
        webhook_secret.encode(),
        webhook_body.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, webhook_signature):
        return jsonify({'error': 'Invalid signature'}), 400

    event = request.get_json(silent=True) or {}
    event_type = event.get('event', '')

    if event_type == 'subscription.activated':
        payload = event.get('payload', {}).get('subscription', {}).get('entity', {})
        notes = payload.get('notes', {})
        user_id = notes.get('user_id')
        if user_id:
            from app.models.user import User
            user = db.session.get(User, int(user_id))
            if user:
                user.is_premium = True
                user.razorpay_subscription_id = payload.get('id')
                db.session.commit()

    elif event_type == 'subscription.cancelled':
        payload = event.get('payload', {}).get('subscription', {}).get('entity', {})
        sub_id = payload.get('id')
        if sub_id:
            from app.models.user import User
            user = User.query.filter_by(razorpay_subscription_id=sub_id).first()
            if user:
                user.is_premium = False
                user.subscription_tier = 'free'
                db.session.commit()

    return jsonify({'status': 'ok'})
