from hashlib import sha256

from app.application.interfaces.hasher import IPasswordHasher


class PasswordHasher(IPasswordHasher):

    def hash(self, password: str) -> str:
        return sha256(password.encode()).hexdigest()
    

    def verify(self, password: str, hashed_password: str) -> bool:
        return sha256(password.encode()).hexdigest() == hashed_password
