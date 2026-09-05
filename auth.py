import hashlib
import secrets


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """رمز عبور را با PBKDF2 هش می‌کند. اگر salt داده نشود، یکی تصادفی می‌سازد."""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return pwd_hash, salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    calc_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calc_hash, expected_hash)
