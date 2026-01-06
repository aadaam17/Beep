def sign_message(msg, priv_key):
    print(f"[CRYPTO] Signing message: {msg}")
    return "signed_demo"

def verify_signature(msg, signature, pub_key):
    print(f"[CRYPTO] Verifying signature for: {msg}")
    return True
