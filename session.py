# --- Funciones para la sesión (simulado para la versión 0.27.2) ---
# En una aplicación real, se usaría un manejo de sesiones más robusto.
current_user_id = None
logged_in_username = None
remember_me = False

def set_session(user_id, username, remember=False):
    """Establece la información de la sesión del usuario."""
    global current_user_id, logged_in_username, remember_me
    current_user_id = user_id
    logged_in_username = username
    remember_me = remember

def clear_session():
    """Limpia la información de la sesión del usuario."""
    global current_user_id, logged_in_username, remember_me
    current_user_id = None
    logged_in_username = None
    remember_me = False

def is_logged_in():
    """Verifica si hay una sesión de usuario activa."""
    return current_user_id is not None

def get_logged_in_username():
    return logged_in_username


