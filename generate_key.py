import secrets
import base64

def generate_secret_key():
    # Generate a secure random key of 32 bytes (256 bits)
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

if __name__ == '__main__':
    secret_key = generate_secret_key()
    print("\nGenerated Secret Key:")
    print("--------------------")
    print(secret_key)
    print("\nAdd this to your .env file as:")
    print(f"SECRET_KEY={secret_key}\n")
