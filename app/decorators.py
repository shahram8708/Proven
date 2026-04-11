from functools import wraps
from flask import redirect, url_for, abort, flash, request, jsonify
from flask_login import current_user


def _is_ajax_request():
    return (
        request.is_json
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.accept_mimetypes.accept_json
    )


def talent_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.account_type != 'talent':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def employer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.account_type != 'employer':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def premium_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            if _is_ajax_request():
                return jsonify({'error': 'Please log in to continue.'}), 401
            return redirect(url_for('auth.login'))
        if not current_user.is_premium:
            if _is_ajax_request():
                return jsonify({'error': 'This feature requires a premium subscription.'}), 403
            flash('This feature requires a premium subscription.', 'warning')
            return redirect(url_for('settings.billing_overview'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def verified_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_email_verified:
            flash('Please verify your email address first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
