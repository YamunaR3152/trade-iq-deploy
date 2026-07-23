import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

# Pull REDIS_URL from .env for shared rate-limiting
_redis_url = os.getenv("REDIS_URL", "").strip()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URL", "memory://"), # Default to memory if env not set
    in_memory_fallback_enabled=True,                 # Fallback to RAM if Redis drops/fails
)
  