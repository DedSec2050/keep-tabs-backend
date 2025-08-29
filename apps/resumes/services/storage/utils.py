import uuid

def sanitize_filename(filename: str) -> str:
    if not filename:
        return "file"
    filename = filename.split("/")[-1].split("\\")[-1]
    # allow alnum, dot, dash, underscore, space, parentheses
    safe = "".join(c for c in filename if c.isalnum() or c in "._-() ")
    return safe[:255] or "file"

def generate_storage_key(user_id, original_filename):
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1]
    return f"users/{user_id}/resumes/{uuid.uuid4().hex}{ext}"
