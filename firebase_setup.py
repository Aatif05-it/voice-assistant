import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("C:\\Users\\KHAN\\Desktop\\python_Ass\\firebase_config.json")  # Ensure correct path
    firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Function to register user
def register_user(email, password, name):
    # Using the filter keyword for the query
    users_ref = db.collection("users").where("email", "==", email).stream()

    for user in users_ref:
        return "User already exists!"

    # Adding the new user
    new_user_ref = db.collection("users").add({
        "name": name,
        "email": email,
        "password": password  # ⚠ Storing passwords as plaintext is unsafe! Use hashing.
    })

    return "User registered successfully!"

# Function to login user
def login_user(email):
    # Using the filter keyword for the query
    users_ref = db.collection("users").where("email", "==", email).stream()
    
    for user in users_ref:
        return user.id  # Return user ID if found

    return None  # No user found

# Example usage:
if __name__ == "__main__":
    print(register_user("testuser@gmail.com", "TestPassword123", "John Doe"))  # Register user
    print(login_user("testuser@gmail.com"))  # Login user
