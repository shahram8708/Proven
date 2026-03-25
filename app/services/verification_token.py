import hashlib
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_email_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
    return serializer.dumps(email_hash, salt='email-verify')


def verify_email_token(token, max_age=172800):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email_hash = serializer.loads(token, salt='email-verify', max_age=max_age)
        return email_hash
    except Exception:
        return None


def generate_password_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
    return serializer.dumps(email_hash, salt='password-reset')


def verify_password_reset_token(token, max_age=172800):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email_hash = serializer.loads(token, salt='password-reset', max_age=max_age)
        return email_hash
    except Exception:
        return None


def generate_verification_token(verification_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(verification_id, salt='verifier-response')


def verify_verification_token(token, max_age=1209600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        verification_id = serializer.loads(token, salt='verifier-response', max_age=max_age)
        return verification_id
    except Exception:
        return None
