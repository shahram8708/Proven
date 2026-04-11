from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.extensions import db
from app.decorators import admin_required
from app.models.user import User
from app.models.evidence import EvidenceSubmission
from app.models.verification import Verification
from app.models.challenge import ChallengeSubmission
from app.models.connection import ContactRequest

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@admin_required
def admin_index():
    stats = {
        'total_users': User.query.count(),
        'total_evidence': EvidenceSubmission.query.count(),
        'total_verifications': Verification.query.count(),
        'fraud_flagged': EvidenceSubmission.query.filter(
            EvidenceSubmission.fraud_flag_level.in_(['medium', 'high'])
        ).count(),
        'talent_count': User.query.filter_by(account_type='talent').count(),
        'employer_count': User.query.filter_by(account_type='employer').count(),
        'verified_emails': User.query.filter_by(is_email_verified=True).count(),
        'active_subscriptions': User.query.filter_by(is_premium=True).count(),
        'published_evidence': EvidenceSubmission.query.filter_by(is_published=True).count(),
        'draft_evidence': EvidenceSubmission.query.filter_by(is_draft=True).count(),
        'challenge_submissions': ChallengeSubmission.query.count(),
        'contact_requests': ContactRequest.query.count(),
    }

    return render_template('admin/index.html', stats=stats)


@admin_bp.route('/admin/users')
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    account_type = request.args.get('account_type', '')

    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
            )
        )
    if account_type:
        query = query.filter_by(account_type=account_type)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template('admin/users.html', users=users, search=search, account_type=account_type)


@admin_bp.route('/admin/fraud')
@admin_required
def fraud_queue():
    flagged = EvidenceSubmission.query.filter(
        EvidenceSubmission.fraud_flag_level.in_(['medium', 'high'])
    ).order_by(EvidenceSubmission.submitted_at.desc()).all()
    return render_template('admin/fraud_queue.html', flagged=flagged)


@admin_bp.route('/admin/evidence/<int:id>/review', methods=['GET', 'POST'])
@admin_required
def admin_review_evidence(id):
    evidence = EvidenceSubmission.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            evidence.fraud_flag_level = 'clean'
            flash('Evidence approved.', 'success')
        elif action == 'reject':
            evidence.is_published = False
            evidence.fraud_flag_level = 'high'
            flash('Evidence rejected and unpublished.', 'warning')
        elif action == 'ban':
            evidence.is_published = False
            evidence.fraud_flag_level = 'high'
            user = User.query.get(evidence.user_id)
            if user:
                user.is_email_verified = False
            flash('Evidence rejected and user suspended.', 'danger')
        db.session.commit()
        return redirect(url_for('admin.fraud_queue'))

    return render_template('admin/fraud_queue.html', flagged=[evidence], reviewing=True)
