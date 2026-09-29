import base64
import hashlib

import bcrypt

# Password hashing uses bcrypt directly (the maintained reference library).
# passlib 1.7.4 is unmaintained and incompatible with bcrypt >= 4.1 (it reads the
# removed ``bcrypt.__about__`` and its backend self-test fails against bcrypt 5.x
# with "password cannot be longer than 72 bytes"), so we do not depend on it.
#
# bcrypt silently truncates inputs at 72 bytes and stops at the first NUL byte.
# Pre-hashing the password with SHA-256 and base64-encoding it removes the length
# limit and avoids NUL truncation while keeping the value (44 bytes) well within
# bcrypt's 72-byte budget.

_BCRYPT_ROUNDS = 12


def _prepare(password: str) -> bytes:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare(password), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(_prepare(password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
