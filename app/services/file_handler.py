import os
import uuid
import logging
from flask import current_app, url_for

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _storage_backend():
    """Return the active storage backend from config ('local' or 's3')."""
    return current_app.config.get('STORAGE_BACKEND', 'local')


def _upload_folder():
    return current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))


def get_s3_client():
    import boto3
    return boto3.client(
        's3',
        region_name=current_app.config.get('AWS_S3_REGION', 'ap-south-1'),
        aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
    )


# ---------------------------------------------------------------------------
#  Validation
# ---------------------------------------------------------------------------

def validate_file(file_storage):
    if not file_storage or not file_storage.filename:
        return False, 'No file selected.'

    file_storage.seek(0, 2)
    size = file_storage.tell()
    file_storage.seek(0)

    if size > MAX_FILE_SIZE:
        return False, f'File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)}MB.'

    try:
        import magic
        header = file_storage.read(2048)
        file_storage.seek(0)
        mime = magic.from_buffer(header, mime=True)
    except ImportError:
        import mimetypes
        mime, _ = mimetypes.guess_type(file_storage.filename)

    if mime not in ALLOWED_MIME_TYPES:
        return False, f'File type {mime} is not allowed.'

    return True, mime


# ---------------------------------------------------------------------------
#  Upload  –  auto-switches between local and S3
# ---------------------------------------------------------------------------

def upload_file(file_storage, user_id, evidence_id):
    """Upload a file using the configured storage backend.

    Returns (result_dict, error_string).  On success error_string is None.
    """
    if _storage_backend() == 's3':
        return _upload_to_s3(file_storage, user_id, evidence_id)
    return _upload_to_local(file_storage, user_id, evidence_id)


# Keep legacy name as an alias
upload_to_s3 = lambda fs, uid, eid: upload_file(fs, uid, eid)


def _upload_to_local(file_storage, user_id, evidence_id):
    """Save file to local uploads/ folder."""
    valid, result = validate_file(file_storage)
    if not valid:
        return None, result

    mime_type = result
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'bin'
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    relative_path = os.path.join('evidence', str(user_id), str(evidence_id))
    full_dir = os.path.join(_upload_folder(), relative_path)
    os.makedirs(full_dir, exist_ok=True)

    full_path = os.path.join(full_dir, safe_filename)
    file_storage.save(full_path)

    # storage_path stores the relative path from uploads/
    storage_path = os.path.join(relative_path, safe_filename).replace('\\', '/')
    file_type = 'image' if mime_type.startswith('image/') else 'pdf' if mime_type == 'application/pdf' else 'document'
    file_size = os.path.getsize(full_path)

    return {
        'storage_path': storage_path,
        'file_type': file_type,
        'original_filename': file_storage.filename,
        'file_size_bytes': file_size,
    }, None


def _upload_to_s3(file_storage, user_id, evidence_id):
    """Upload file to AWS S3."""
    from botocore.exceptions import ClientError

    valid, result = validate_file(file_storage)
    if not valid:
        return None, result

    mime_type = result
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else 'bin'
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    s3_key = f"evidence/{user_id}/{evidence_id}/{safe_filename}"

    try:
        client = get_s3_client()
        bucket = current_app.config.get('AWS_S3_BUCKET', 'proven-evidence-files')
        client.upload_fileobj(
            file_storage,
            bucket,
            s3_key,
            ExtraArgs={'ContentType': mime_type, 'ServerSideEncryption': 'AES256'},
        )
        file_storage.seek(0, 2)
        file_size = file_storage.tell()
        file_type = 'image' if mime_type.startswith('image/') else 'pdf' if mime_type == 'application/pdf' else 'document'
        return {
            'storage_path': s3_key,
            'file_type': file_type,
            'original_filename': file_storage.filename,
            'file_size_bytes': file_size,
        }, None
    except ClientError as exc:
        logger.error("S3 upload failed: %s", exc)
        return None, 'File upload failed. Please try again.'


# ---------------------------------------------------------------------------
#  Get file URL  –  auto-switches between local and S3
# ---------------------------------------------------------------------------

def get_file_url(storage_path, expiry=3600):
    """Return a URL to access the file.

    For local storage returns a static-file URL.
    For S3 returns a pre-signed URL.
    """
    if not storage_path:
        return None

    if _storage_backend() == 's3':
        return _get_presigned_url(storage_path, expiry)
    return _get_local_url(storage_path)


# Keep legacy name as alias
get_presigned_url = lambda key, expiry=3600: get_file_url(key, expiry)


def _get_local_url(storage_path):
    """Return URL for a locally stored file served via /uploads/... route."""
    return f'/uploads/{storage_path}'


def _get_presigned_url(s3_key, expiry=3600):
    """Generate a pre-signed S3 URL."""
    from botocore.exceptions import ClientError

    try:
        client = get_s3_client()
        bucket = current_app.config.get('AWS_S3_BUCKET', 'proven-evidence-files')
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': s3_key},
            ExpiresIn=expiry,
        )
        return url
    except ClientError as exc:
        logger.error("Failed to generate presigned URL: %s", exc)
        return None


# ---------------------------------------------------------------------------
#  Delete file  –  auto-switches between local and S3
# ---------------------------------------------------------------------------

def delete_file(storage_path):
    """Delete a file from whichever backend it was stored on."""
    if not storage_path:
        return

    if _storage_backend() == 's3':
        _delete_from_s3(storage_path)
    else:
        _delete_from_local(storage_path)


def _delete_from_local(storage_path):
    full_path = os.path.join(_upload_folder(), storage_path)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except OSError as exc:
        logger.error("Failed to delete local file: %s", exc)


def _delete_from_s3(s3_key):
    from botocore.exceptions import ClientError

    try:
        client = get_s3_client()
        bucket = current_app.config.get('AWS_S3_BUCKET', 'proven-evidence-files')
        client.delete_object(Bucket=bucket, Key=s3_key)
    except ClientError as exc:
        logger.error("Failed to delete S3 object: %s", exc)
