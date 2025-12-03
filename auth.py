from functools import wraps
from flask import session, jsonify, redirect, url_for

def login_required(f):
    """Decoratore per richiedere autenticazione"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Autenticazione richiesta'}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    """Decoratore per richiedere un ruolo specifico"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'error': 'Autenticazione richiesta'}), 401
            if session.get('user', {}).get('role') != role:
                return jsonify({'error': 'Accesso negato'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def login_user(user_data):
    """Salva l'utente nella sessione"""
    session['user'] = {
        'id': user_data['id'],
        'name': user_data['name'],
        'email': user_data['email'],
        'role': user_data['role']
    }

def logout_user():
    """Rimuove l'utente dalla sessione"""
    session.pop('user', None)

def current_user():
    """Ritorna l'utente corrente dalla sessione"""
    return session.get('user')
