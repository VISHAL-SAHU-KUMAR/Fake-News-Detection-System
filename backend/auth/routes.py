from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.crud import create_user, get_user_by_email, set_user_otp, verify_user_account, update_user_password
from database.models import UserCreate, UserLogin, UserResponse, VerifyOTP, ForgotPassword, ResetPassword, UserProfileUpdate, DeleteAccountRequest, DeleteAccountConfirm, IdentityKeyRequest, CancelDeletionRequest
from auth.utils import get_password_hash, verify_password, create_access_token, decode_access_token
from utils.email_service import send_otp_email, send_welcome_email, send_identity_key_msg, send_deletion_scheduled_email, send_deletion_cancelled_email
import random
import string
from datetime import datetime, timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_optional_user(token: str = None):
    """Dependency to return the current user if a valid token is provided, or None."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        email = payload.get("sub")
        return await get_user_by_email(email)
    except:
        return None

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_dict["analyses_count"] = 0
    user_dict["created_at"] = datetime.utcnow()
    
    created_user = await create_user(user_dict)
    if not created_user:
        raise HTTPException(status_code=500, detail="Database error or not configured")
    
    # Registration successful, generate alphanumeric OTP and send
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    user_id_str = str(created_user["id"])
    
    await set_user_otp(user_id_str, otp)
    
    # Send email (in a background task ideally, but for now we call it directly)
    send_otp_email(created_user["email"], otp)
    
    return {
        "id": user_id_str,
        "email": created_user["email"],
        "name": created_user["name"],
        "is_verified": False,
        "analyses_count": created_user["analyses_count"],
        "created_at": created_user["created_at"]
    }

@router.post("/verify-otp")
async def verify_otp(data: VerifyOTP):
    user = await get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.get("is_verified"):
        return {"msg": "Already verified"}
        
    if user.get("otp_code") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    await verify_user_account(str(user["id"]))
    
    # Send Welcome Identity Kit
    send_welcome_email(user["email"], user["name"], str(user["id"]))
    
    # Generate token immediately after verify
    access_token = create_access_token(data={"sub": user["email"], "id": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer", "msg": "Identity Verified. Welcome Operative.", "user": {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"]
    }}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    user = await get_user_by_email(data.email)
    if not user:
        return {"msg": "If an account exists, an OTP has been sent."}
        
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    await set_user_otp(str(user["id"]), otp)
    send_otp_email(user["email"], otp)
    return {"msg": "If an account exists, an OTP has been sent."}

@router.post("/resend-otp")
async def resend_otp(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
        
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.get("is_verified"):
        return {"msg": "Account already verified"}
        
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    await set_user_otp(str(user["id"]), otp)
    send_otp_email(email, otp)
    
    return {"msg": "New Alphanumeric OTP dispatched to your node."}

@router.post("/reset-password")
async def reset_password(data: ResetPassword):
    user = await get_user_by_email(data.email)
    if not user or user.get("otp_code") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    hashed_pwd = get_password_hash(data.new_password)
    await update_user_password(str(user["id"]), hashed_pwd)
    return {"msg": "Password updated successfully."}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not db_user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Account not verified. Please verify your email via OTP.")
        
    # Check if 48h deletion period passed
    if db_user.get("deletion_at"):
        del_at = datetime.fromisoformat(db_user["deletion_at"].replace('Z', '+00:00')) if isinstance(db_user["deletion_at"], str) else db_user["deletion_at"]
        # Ensure del_at is naive for comparison if utcnow is naive, or both aware. 
        # Supabase usually gives awareness.
        if datetime.utcnow().replace(tzinfo=del_at.tzinfo if del_at.tzinfo else None) > del_at.replace(tzinfo=del_at.tzinfo if del_at.tzinfo else None):
            from database.crud import delete_user
            await delete_user(db_user["email"])
            raise HTTPException(status_code=410, detail="Account purged after 48h grace period.")

    access_token = create_access_token(data={"sub": db_user["email"], "id": str(db_user["id"])})
    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": str(db_user["id"]),
        "email": db_user["email"],
        "name": db_user["name"]
    }}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["id"]),
        "email": current_user["email"],
        "name": current_user["name"],
        "phone": current_user.get("phone"),
        "bio": current_user.get("bio"),
        "linked_in": current_user.get("linked_in"),
        "profile_photo": current_user.get("profile_photo"),
        "is_verified": current_user.get("is_verified", False),
        "analyses_count": current_user.get("analyses_count", 0),
        "created_at": current_user.get("created_at"),
        "deletion_at": current_user.get("deletion_at")
    }

@router.post("/update-profile")
async def update_profile(data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    # Filter out None AND empty strings for mandatory fields like name
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # If name is provided but empty, remove it to avoid NOT NULL error
    if "name" in update_data and not update_data["name"].strip():
        del update_data["name"]
        
    if not update_data:
        return {"msg": "No changes provided or invalid data"}
        
    from database.crud import update_user_profile
    success = await update_user_profile(user_id, update_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
        
    return {"msg": "Profile updated successfully"}

@router.post("/delete-request")
async def delete_request(data: DeleteAccountRequest, current_user: dict = Depends(get_current_user)):
    if data.email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    # Generate 6-char Alphanumeric OTP for deletion
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    from database.crud import set_delete_otp
    from utils.email_service import send_delete_otp_email
    
    await set_delete_otp(data.email, otp)
    send_delete_otp_email(data.email, otp)
    
    return {"msg": "Alphanumeric security OTP sent to your email"}

@router.post("/delete-confirm")
async def delete_confirm(data: DeleteAccountConfirm, current_user: dict = Depends(get_current_user)):
    if data.email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    # Verify both OTP and Identity Key
    if current_user.get("otp_delete") != data.otp:
        raise HTTPException(status_code=400, detail="Invalid security OTP")
        
    if data.identity_key != str(current_user["id"]):
        raise HTTPException(status_code=400, detail="Invalid Operative Identity Key")
        
    from database.crud import schedule_account_deletion
    from utils.email_service import send_deletion_scheduled_email
    
    # Schedule for 48 hours from now
    deletion_time = datetime.utcnow() + timedelta(hours=48)
    success = await schedule_account_deletion(data.email, deletion_time)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to schedule neutralization")
        
    send_deletion_scheduled_email(data.email)
    return {"msg": "Neutralization scheduled. Active for 48 hours before purge. Appeal email sent."}

@router.post("/cancel-deletion")
async def cancel_deletion(data: CancelDeletionRequest, current_user: dict = Depends(get_current_user)):
    if data.email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    from database.crud import cancel_account_deletion
    from utils.email_service import send_deletion_cancelled_email
    
    success = await cancel_account_deletion(data.email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to terminate neutralization")
        
    send_deletion_cancelled_email(data.email)
    return {"msg": "Neutralization terminated. Node recovered successfully."}

@router.post("/request-identity")
async def request_identity(data: IdentityKeyRequest, current_user: dict = Depends(get_current_user)):
    if data.email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    send_identity_key_msg(current_user["email"], str(current_user["id"]))
    return {"msg": "Operative Identity Key dispatched to your email."}
