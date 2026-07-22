import uuid
from pathlib import Path

from app.core.config import settings


def save_file(filename: str, file_bytes: bytes) -> str:
    """Saves file bytes to disk under a UUID-based name. Returns the stored filename."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    stored_filename = f"{uuid.uuid4()}.{ext}"

    (upload_dir / stored_filename).write_bytes(file_bytes)
    return stored_filename
