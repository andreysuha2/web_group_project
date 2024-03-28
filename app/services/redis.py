import redis
from app.settings import settings

redis_client = redis.Redis(
    host = settings.redis.HOST,
    port = settings.redis.PORT,
    db = settings.redis.DB,
    encoding = settings.redis.ENCODING,
    decode_responses = True
)