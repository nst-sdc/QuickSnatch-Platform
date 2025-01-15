from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

def hash_password(password):
    """Hash a password using Werkzeug's generate_password_hash"""
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    return generate_password_hash(password)

def check_password(stored_password, provided_password):
    """
    Check if the provided password matches the stored password hash.
    Handles both old bcrypt hashes and new Werkzeug hashes.
    """
    # Convert bytes to string if necessary
    if isinstance(stored_password, bytes):
        stored_password = stored_password.decode('utf-8')
    if isinstance(provided_password, bytes):
        provided_password = provided_password.decode('utf-8')

    # Try Werkzeug hash first
    try:
        return check_password_hash(stored_password, provided_password)
    except Exception:
        # If that fails, try bcrypt
        try:
            return bcrypt.checkpw(
                provided_password.encode('utf-8'),
                stored_password.encode('utf-8')
            )
        except Exception:
            return False

def migrate_password_if_needed(mongo_db, user_id, password):
    """
    Migrate password to new hashing scheme if needed.
    Returns True if migration was performed, False otherwise.
    """
    user = mongo_db.users.find_one({'_id': user_id})
    if not user:
        return False

    stored_password = user.get('password', '')
    if isinstance(stored_password, bytes):
        stored_password = stored_password.decode('utf-8')

    # Check if it's a bcrypt hash
    if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
        # Only migrate if the password is correct
        if bcrypt.checkpw(
            password.encode('utf-8'),
            stored_password.encode('utf-8')
        ):
            # Migrate to new hash
            new_hash = hash_password(password)
            mongo_db.users.update_one(
                {'_id': user_id},
                {'$set': {'password': new_hash}}
            )
            return True
    return False
