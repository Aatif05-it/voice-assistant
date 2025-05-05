import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")  
    firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Function to Add User
def add_user(email, password, name):
    user_ref = db.collection("users").document(email)
    user_ref.set({
        "email": email,
        "password": password,  # Store hashed password in real projects!
        "name": name,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    print(f"✅ User {name} added successfully!")

# Function to Get User
def get_user(email):
    user_ref = db.collection("users").document(email)
    user = user_ref.get()
    if user.exists:
        print(f"✅ User found: {user.to_dict()}")
        return user.to_dict()
    else:
        print("❌ User not found!")
        return None

# Example Usage
if __name__ == "__main__":
    add_user("testuser@gmail.com", "Test@1234", "John Doe")  # Add user
    get_user("testuser@gmail.com")  # Retrieve user
