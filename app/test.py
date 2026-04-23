# test.py
import sys
sys.path.append(".")

from services.auth import hash_password, verify_password

pwd = "monmotdepasse"
hashed = hash_password(pwd)
print(f"Hash: {hashed}")

result = verify_password(pwd, hashed)
print(f"Résultat: {result}")  # doit afficher True