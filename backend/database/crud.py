from database.connection import get_db
import traceback

async def create_user(user_data: dict):
    db = get_db()
    if not db:
        print("ERROR: create_user called but Supabase client is None (not connected).")
        return None
    try:
        if "created_at" in user_data and hasattr(user_data["created_at"], "isoformat"):
            user_data["created_at"] = user_data["created_at"].isoformat()

        print(f"DEBUG create_user: Inserting user with email={user_data.get('email')}")
        response = db.table("users").insert(user_data).execute()
        print(f"DEBUG create_user: Supabase response: {response}")
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}\n{traceback.format_exc()}")
        return None

async def get_user_by_email(email: str):
    db = get_db()
    if not db: return None
    try:
        response = db.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching user: {e}\n{traceback.format_exc()}")
        return None

async def save_analysis(analysis_data: dict):
    db = get_db()
    if not db: return None
    try:
        if "created_at" in analysis_data and hasattr(analysis_data["created_at"], "isoformat"):
            analysis_data["created_at"] = analysis_data["created_at"].isoformat()
        response = db.table("analyses").insert(analysis_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error saving analysis: {e}\n{traceback.format_exc()}")
        return None

async def get_analyses_by_user(user_id: str, limit: int = 20):
    db = get_db()
    if not db: return []
    try:
        response = db.table("analyses").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error getting history: {e}")
        return []

async def get_trending_analyses(limit: int = 10):
    db = get_db()
    if not db: return []
    try:
        response = db.table("analyses").select("*").in_("verdict", ["FALSE", "MISLEADING"]).lt("score", 40).order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error getting trending: {e}")
        return []

async def set_user_otp(user_id: str, otp: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update({"otp_code": otp}).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error setting OTP: {e}")
        return False

async def verify_user_account(user_id: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update({"is_verified": True, "otp_code": None}).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

async def update_user_profile(user_id: str, profile_data: dict):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update(profile_data).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

async def set_delete_otp(email: str, otp: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update({"otp_delete": otp}).eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error setting delete OTP: {e}")
        return False

async def delete_user(email: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").delete().eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

async def schedule_account_deletion(email: str, deletion_time):
    db = get_db()
    if not db: return False
    try:
        if hasattr(deletion_time, "isoformat"):
            deletion_time = deletion_time.isoformat()
        db.table("users").update({"deletion_at": deletion_time, "otp_delete": None}).eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error scheduling deletion: {e}")
        return False

async def cancel_account_deletion(email: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update({"deletion_at": None, "otp_delete": None}).eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error cancelling deletion: {e}")
        return False

async def update_user_password(user_id: str, new_password_hash: str):
    db = get_db()
    if not db: return False
    try:
        db.table("users").update({"password_hash": new_password_hash, "otp_code": None}).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False