from django.core.cache import cache


def store_user_id_in_cache(self, user_id):
    # Use both the user ID and the session ID to create a unique cache key
    cache_key = f"websocket_user_{user_id}_{self.session_id}"
    cache.set(cache_key, user_id, timeout=3600)
