import secrets

# Generate a secure secret key
secret_key = secrets.token_hex(32)
print(f"\nSECRET_KEY for .env file:")
print(f"SECRET_KEY={secret_key}\n")
