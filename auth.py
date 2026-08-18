"""
Gestion des comptes utilisateurs (inscription / connexion).
Les utilisateurs sont stockés dans un fichier JSON (users.json).
Les mots de passe ne sont JAMAIS stockés en clair : on stocke un sel
aléatoire + le hash SHA-256 de (sel + mot de passe).
"""

import json
import os
import hashlib
import secrets

USERS_FILE = "users.json"


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def register_user(username, password):
    """Crée un nouveau compte. Retourne (succes: bool, message: str)."""
    users = _load_users()

    if username in users:
        return False, "Ce nom d'utilisateur existe déjà."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    users[username] = {"salt": salt, "password_hash": password_hash}
    _save_users(users)
    return True, "Compte créé avec succès. Vous pouvez vous connecter."


def authenticate_user(username, password):
    """Vérifie les identifiants. Retourne True/False."""
    users = _load_users()
    user = users.get(username)
    if not user:
        return False

    expected_hash = _hash_password(password, user["salt"])
    return expected_hash == user["password_hash"]

