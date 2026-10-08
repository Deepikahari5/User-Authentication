
import sqlite3

conn = sqlite3.connect("users.db")
rows = conn.execute("SELECT user_id, email, password_hash FROM users").fetchall()
conn.close()

if not rows:
    print("No users found. Register a user first.")
for user_id, email, password_hash in rows:
    print(f"User {user_id} | {email}")
    print(f"   stored value : {password_hash}")
    print(f"   is hashed    : {password_hash.startswith('pbkdf2_sha256$')}")
    print()
