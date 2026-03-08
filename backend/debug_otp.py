import os
import asyncio
from database.connection import init_db, get_db

async def find_otp(email):
    await init_db()
    db = get_db()
    if not db:
        print("Not connected to DB")
        return
    
    res = db.table("users").select("otp_code").eq("email", email).execute()
    if res.data:
        print(f"OTP for {email}: {res.data[0]['otp_code']}")
    else:
        print(f"User {email} not found")

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "testp9z49v@example.com"
    asyncio.run(find_otp(email))
