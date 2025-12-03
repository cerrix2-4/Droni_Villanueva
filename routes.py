from flask import Blueprint, render_template
from auth import login_required, role_required

web = Blueprint('web', __name__)

@web.route('/')
def home():
    """Pagina pubblica landing"""
    return render_template('index.html')

@web.route('/login')
def login():
    """Pagina login"""
    return render_template('login.html')

@web.route('/register')
def register():
    """Pagina registrazione"""
    return render_template('register.html')

@web.route('/customer')
@login_required
@role_required('customer')
def customer():
    """Dashboard cliente protetta"""
    return render_template('customer.html')

@web.route('/admin')
@login_required
@role_required('admin')
def admin():
    """Dashboard admin protetta"""
    return render_template('admin.html')
