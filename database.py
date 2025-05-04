import sqlite3
import hashlib

DATABASE_FILE = "users.db"

def create_tables():
    """Crea las tablas de la base de datos si no existen."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expiry_timestamp REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashea la contraseña utilizando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    """Verifica si la contraseña coincide con el hash almacenado."""
    return stored_hash == hash_password(password)

def insert_user(username, email, phone, password):
    """Inserta un nuevo usuario en la base de datos."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                        (username, email, phone, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Registro exitoso"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El nombre de usuario o el correo electrónico ya existen."

def fetch_user(username):
    """Obtiene los datos de un usuario por su nombre de usuario."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


