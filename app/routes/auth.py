import hashlib
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.models.employer import EmployerAccount
from app.forms.auth_forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.services.verification_token import (
    generate_email_verification_token,
    verify_email_token,
    generate_password_reset_token,
    verify_password_reset_token,
)
from app.services.email_service import send_email_verification, send_password_reset

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5/hour")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower().strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            username=form.username.data.lower().strip(),
            account_type=form.account_type.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        if user.account_type == 'employer':
            employer = EmployerAccount(
                owner_user_id=user.id,
                company_name=f"{user.first_name}'s Company",
                monthly_contact_credits=3,
            )
            db.session.add(employer)

        db.session.commit()

        token = generate_email_verification_token(user.email)
        send_email_verification(user, token)

        flash('Account created! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10/15minutes")
def login():
    if current_user.is_authenticated:
        if current_user.account_type == 'employer':
            return redirect(url_for('employer_dashboard.employer_dashboard'))
        return redirect(url_for('talent_dashboard.talent_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            # Force a long-lived login cookie (1 year) until the user explicitly logs out.
            login_user(
                user,
                remember=True,
                duration=current_app.config.get('REMEMBER_COOKIE_DURATION'),
            )

            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None

            if next_page:
                return redirect(next_page)

            if not user.onboarding_complete:
                return redirect(url_for('onboarding.onboarding_step1'))

            if user.account_type == 'employer':
                return redirect(url_for('employer_dashboard.employer_dashboard'))
            elif user.is_admin:
                return redirect(url_for('admin.admin_index'))
            return redirect(url_for('talent_dashboard.talent_dashboard'))

        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify/<token>')
def verify_email(token):
    email_hash = verify_email_token(token)
    if email_hash is None:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()
    target_user = None
    for u in users:
        if hashlib.sha256(u.email.lower().encode()).hexdigest() == email_hash:
            target_user = u
            break

    if target_user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    target_user.is_email_verified = True
    db.session.commit()
    flash('Your email has been verified! You can now log in.', 'success')
    return render_template('auth/email_verified.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5/hour")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            token = generate_password_reset_token(user.email)
            send_password_reset(user, token)
        flash('If an account with that email exists, we have sent a password reset link.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email_hash = verify_password_reset_token(token)
    if email_hash is None:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        users = User.query.all()
        target_user = None
        for u in users:
            if hashlib.sha256(u.email.lower().encode()).hexdigest() == email_hash:
                target_user = u
                break

        if target_user:
            target_user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, token=token)
