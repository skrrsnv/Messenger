

class PresenceService:
    def __init__(self, redis_client):
        self.redis = redis_client

    @staticmethod
    def _key(user_id: int) -> str:
        return f"presence:user:{user_id}:connections"

    async def connect(
        self,
        user_id: int,
        connection_id: str,
    ) -> bool:
        result = await self.redis.eval(
            """
            local added = redis.call('SADD', KEYS[1], ARGV[1])
            local count = redis.call('SCARD', KEYS[1])

            if added == 1 and count == 1 then
                return 1
            end

            return 0
            """,
            1,
            self._key(user_id),
            connection_id,
        )
        return bool(result)

    async def disconnect(
        self,
        user_id: int,
        connection_id: str,
    ) -> bool:
        result = await self.redis.eval(
            """
            redis.call('SREM', KEYS[1], ARGV[1])
            return redis.call('SCARD', KEYS[1])
            """,
            1,
            self._key(user_id),
            connection_id,
        )
        return result == 0

    async def is_online(self, user_id: int) -> bool:
        return bool(
            await self.redis.exists(self._key(user_id))
        )
