from django.core.cache import cache

def set_user_online(user_id):
    cache.set(f"presence:user:{user_id}", "online", timeout=300)
    
def set_user_offline(user_id):
    cache.set(f"presence:user:{user_id}", "offline", timeout=300)
    
def is_user_online(user_id):
    return cache.get(f"presence:user:{user_id}") == "online"

