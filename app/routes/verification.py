from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.decorators import talent_required
from app.models.evidence import EvidenceSubmission
from app.models.verification import Verification
from app.forms.verification_forms import VerificationRequestForm, VerifierResponseForm
from app.services.verification_token import generate_verification_token
from app.services.email_service import send_verification_request_to_verifier

verification_bp = Blueprint('verification', __name__)


@verification_bp.route('/verify/request/<int:evidence_id>', methods=['GET', 'POST'])
@talent_required
@limiter.limit("20/day")
def request_verification(evidence_id):
    evidence = EvidenceSubmission.query.get_or_404(evidence_id)
    if evidence.user_id != current_user.id:
        abort(403)

    form = VerificationRequestForm()
    if form.validate_on_submit():
        token = generate_verification_token(evidence.id)

        verification = Verification(
            evidence_id=evidence.id,
            requester_user_id=current_user.id,
            verifier_email=form.verifier_email.data.strip().lower(),
            verifier_name=form.verifier_name.data.strip(),
            verifier_role=form.verifier_role.data.strip() if form.verifier_role.data else None,
            verifier_company=form.verifier_company.data.strip() if form.verifier_company.data else None,
            specific_claim=form.specific_claim.data.strip(),
            token=token,
            token_expires=datetime.utcnow() + timedelta(days=14),
        )
        db.session.add(verification)
        db.session.commit()

        send_verification_request_to_verifier(verification, evidence)

        flash('Verification request sent!', 'success')
        return redirect(url_for('evidence.evidence_detail', id=evidence.id))

    return render_template('verification/request.html', form=form, evidence=evidence)


@verification_bp.route('/verify/respond/<token>', methods=['GET', 'POST'])
def verifier_response(token):
    verification = Verification.query.filter_by(token=token).first()
    if not verification:
        flash('Invalid verification link.', 'danger')
        return redirect(url_for('main.index'))

    if verification.token_expires < datetime.utcnow():
        flash('This verification link has expired.', 'warning')
        return redirect(url_for('main.index'))

    if verification.response != 'pending':
        flash('This verification has already been responded to.', 'info')
        return render_template('verification/respond.html', verification=verification, already_responded=True)

    evidence = EvidenceSubmission.query.get(verification.evidence_id)
    form = VerifierResponseForm()

    if form.validate_on_submit():
        verification.response = form.response.data
        verification.qualification_text = form.qualification_text.data.strip() if form.qualification_text.data else None
        verification.responded_at = datetime.utcnow()

        if verification.response in ('confirmed', 'confirmed_with_qualification'):
            evidence.verification_count = (evidence.verification_count or 0) + 1

        db.session.commit()

        flash('Thank you for your verification response.', 'success')
        return render_template('verification/respond.html', verification=verification, already_responded=True)

    return render_template('verification/respond.html', form=form, verification=verification, evidence=evidence, already_responded=False)


@verification_bp.route('/verify/status/<int:evidence_id>')
@login_required
def verification_status(evidence_id):
    evidence = EvidenceSubmission.query.get_or_404(evidence_id)
    if evidence.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    verifications = Verification.query.filter_by(evidence_id=evidence_id).all()
    data = []
    for v in verifications:
        data.append({
            'id': v.id,
            'verifier_name': v.verifier_name,
            'verifier_role': v.verifier_role,
            'verifier_company': v.verifier_company,
            'response': v.response,
            'responded_at': v.responded_at.isoformat() if v.responded_at else None,
            'requested_at': v.requested_at.isoformat() if v.requested_at else None,
        })
    return jsonify({'verifications': data})
