from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding_step1():
    if current_user.onboarding_complete:
        return redirect(url_for('talent_dashboard.talent_dashboard'))
    if request.method == 'POST':
        domain = request.form.get('primary_domain', '').strip()
        if domain:
            current_user.primary_domain = domain
            db.session.commit()
            return redirect(url_for('onboarding.onboarding_step2'))
        flash('Please select your primary domain.', 'warning')
    domains = [
        'Technology', 'Marketing', 'Finance', 'Design',
        'Operations', 'Research', 'Legal', 'Healthcare', 'Education',
    ]
    return render_template('onboarding/step1_domain.html', domains=domains)


@onboarding_bp.route('/onboarding/step2', methods=['GET', 'POST'])
@login_required
def onboarding_step2():
    if current_user.onboarding_complete:
        return redirect(url_for('talent_dashboard.talent_dashboard'))
    if request.method == 'POST':
        years = request.form.get('years_experience', '')
        location_city = request.form.get('location_city', '').strip()
        location_country = request.form.get('location_country', '').strip()
        if years:
            current_user.years_experience = int(years)
            current_user.location_city = location_city
            current_user.location_country = location_country
            db.session.commit()
            return redirect(url_for('onboarding.onboarding_step3'))
        flash('Please enter your years of experience.', 'warning')
    return render_template('onboarding/step2_experience.html')


@onboarding_bp.route('/onboarding/step3', methods=['GET', 'POST'])
@login_required
def onboarding_step3():
    if current_user.onboarding_complete:
        return redirect(url_for('talent_dashboard.talent_dashboard'))
    if request.method == 'POST':
        opportunity_type = request.form.get('opportunity_type', '').strip()
        open_to = request.form.get('open_to_opportunities') == 'on'
        current_user.opportunity_type = opportunity_type
        current_user.open_to_opportunities = open_to
        current_user.onboarding_complete = True
        db.session.commit()
        flash('Onboarding complete! Welcome to Proven.', 'success')
        if current_user.account_type == 'employer':
            return redirect(url_for('employer_dashboard.employer_dashboard'))
        return redirect(url_for('talent_dashboard.talent_dashboard'))
    return render_template('onboarding/step3_goals.html')
