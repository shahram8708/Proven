from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.profile_forms import AccountSettingsForm

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    form = AccountSettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name = form.last_name.data.strip()
        db.session.commit()
        flash('Settings updated.', 'success')
        return redirect(url_for('settings.account_settings'))
    return render_template('settings/account.html', form=form)


@settings_bp.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notification_settings():
    if request.method == 'POST':
        flash('Notification preferences saved.', 'success')
        return redirect(url_for('settings.notification_settings'))
    return render_template('settings/notifications.html')


@settings_bp.route('/settings/billing')
@login_required
def billing_overview():
    return render_template('settings/billing.html')
