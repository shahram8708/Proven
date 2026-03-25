import logging
from flask import current_app, url_for, render_template
from flask_mail import Message
from app.extensions import mail

logger = logging.getLogger(__name__)


def send_email_verification(user, token):
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    msg = Message(
        subject='Verify your Proven account',
        recipients=[user.email],
        html=render_template('emails/email_verification.html', user=user, verify_url=verify_url),
    )
    try:
        mail.send(msg)
    except Exception as exc:
        logger.error("Failed to send verification email to %s: %s", user.email, exc)


def send_password_reset(user, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message(
        subject='Reset your Proven password',
        recipients=[user.email],
        html=render_template('emails/password_reset.html', user=user, reset_url=reset_url),
    )
    try:
        mail.send(msg)
    except Exception as exc:
        logger.error("Failed to send password reset to %s: %s", user.email, exc)


def send_verification_request_to_verifier(verification, evidence):
    respond_url = url_for('verification.verifier_response', token=verification.token, _external=True)
    msg = Message(
        subject=f'Verification request from {evidence.user.full_name} on Proven',
        recipients=[verification.verifier_email],
        html=render_template(
            'emails/verification_request.html',
            verification=verification,
            evidence=evidence,
            respond_url=respond_url,
        ),
    )
    try:
        mail.send(msg)
    except Exception as exc:
        logger.error("Failed to send verification request to %s: %s", verification.verifier_email, exc)


def send_contact_request_to_talent(contact_request, employer_name):
    msg = Message(
        subject=f'{employer_name} wants to connect with you on Proven',
        recipients=[contact_request.talent.email],
        html=render_template(
            'emails/contact_request.html',
            contact_request=contact_request,
            employer_name=employer_name,
        ),
    )
    try:
        mail.send(msg)
    except Exception as exc:
        logger.error("Failed to send contact request email: %s", exc)


def send_verification_received_notification(user, evidence):
    msg = Message(
        subject='You received a new verification on Proven',
        recipients=[user.email],
        html=render_template(
            'emails/email_verification.html',
            user=user,
            verify_url=url_for('evidence.evidence_detail', id=evidence.id, _external=True),
        ),
    )
    try:
        mail.send(msg)
    except Exception as exc:
        logger.error("Failed to send verification notification: %s", exc)
