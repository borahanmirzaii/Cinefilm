"""Usage tracking middleware"""
from functools import wraps
from datetime import datetime
from typing import Optional
from firebase_admin import firestore


def track_usage(action: str, resource_type: Optional[str] = None):
    """
    Decorator to track API usage to Firestore users/{userId}/usage collection
    Records: action, timestamp, duration, resource_type
    Updates monthly quotas in users/{userId}/quotas/current
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            start_time = datetime.utcnow()
            result = await func(*args, **kwargs)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Track usage
            try:
                db = firestore.client()
                
                # Extract user_id from kwargs or request object
                user_id = None
                if "current_user" in kwargs:
                    user_id = kwargs["current_user"].get("uid")
                elif args and hasattr(args[0], "state") and hasattr(args[0].state, "user_id"):
                    user_id = args[0].state.user_id
                elif args and isinstance(args[0], dict) and "uid" in args[0]:
                    user_id = args[0]["uid"]

                if user_id:
                    # Record usage
                    usage_data = {
                        "userId": user_id,
                        "timestamp": firestore.SERVER_TIMESTAMP,
                        "action": action,
                        "resourceType": resource_type,
                        "duration": duration_ms,
                        "metadata": {
                            "endpoint": func.__name__,
                        },
                    }
                    db.collection("users").document(user_id).collection("usage").add(
                        usage_data
                    )

                    # Update monthly quota
                    _update_quota(db, user_id, action, resource_type)
            except Exception as e:
                # Silently fail if tracking fails (don't break the API)
                print(f"Usage tracking error: {e}")

            return result

        return wrapper

    return decorator


def _update_quota(db, user_id: str, action: str, resource_type: Optional[str]):
    """Update monthly quota for user"""
    try:
        now = datetime.utcnow()
        quota_ref = db.collection("users").document(user_id).collection("quotas").document("current")
        quota_doc = quota_ref.get()

        if quota_doc.exists:
            quota_data = quota_doc.to_dict()
            # Update usage counters based on action
            if action == "ai_generation":
                quota_data["usage"]["aiGenerations"] = quota_data["usage"].get("aiGenerations", 0) + 1
            elif action == "asset_upload" and resource_type:
                size_bytes = 0  # Would need to get from request
                quota_data["usage"]["storageBytes"] = quota_data["usage"].get("storageBytes", 0) + size_bytes
            elif action == "drive_import":
                quota_data["usage"]["driveImports"] = quota_data["usage"].get("driveImports", 0) + 1

            quota_ref.update(quota_data)
        else:
            # Create initial quota if doesn't exist
            quota_data = {
                "period": "monthly",
                "startDate": firestore.SERVER_TIMESTAMP,
                "endDate": None,  # Calculate end of month
                "usage": {
                    "aiGenerations": 1 if action == "ai_generation" else 0,
                    "storageBytes": 0,
                    "driveImports": 1 if action == "drive_import" else 0,
                },
                "limits": {
                    "aiGenerations": 10,  # Default Basic plan
                    "storageBytes": 5 * 1024 * 1024 * 1024,  # 5GB
                    "driveImports": 10,
                },
            }
            quota_ref.set(quota_data)
    except Exception as e:
        print(f"Quota update error: {e}")

