import asyncio
from database.connection import get_db
from database.crud import get_user_by_email

async def test_db_cols():
    from database.connection import init_db
    await init_db()
    db = get_db()
    if not db:
        print("Not connected to DB")
        return
    
    # Try a simple update to see the error
    try:
        # We'll try to find any user first
        res = db.table("users").select("id").limit(1).execute()
        if not res.data:
            print("No users found to test update")
            return
        
        uid = res.data[0]['id']
        print(f"Testing update for user ID: {uid}")
        
        # Test updating a single column to find the culprit
        cols = ["phone", "bio", "linked_in", "profile_photo"]
        for col in cols:
            try:
                db.table("users").update({col: "test"}).eq("id", uid).execute()
                print(f"Column '{col}' is OK")
            except Exception as e:
                print(f"Column '{col}' ERROR: {e}")
                
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_cols())
