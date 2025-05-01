"""
Flask QR Code Authentication System

This application provides a complete authentication system with QR code-based
two-factor authentication using Flask.

Required packages:
- flask
- pyotp
- qrcode
- flask-sqlalchemy
- flask-login
- pillow

Install with: pip install flask pyotp qrcode flask-sqlalchemy flask-login pillow
"""

import os
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pyotp
import qrcode

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrauth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Generate QR code as base64 for embedding in HTML
def generate_qr_code(otp_auth_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(otp_auth_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to in-memory bytes buffer
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username, password=password)
        
        # Generate OTP secret
        new_user.otp_secret = pyotp.random_base32()
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please setup 2FA now.', 'success')
        return redirect(url_for('setup_2fa', user_id=new_user.id))
    
    return render_template('register.html')


@app.route('/setup-2fa/<int:user_id>')
def setup_2fa(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))
    
    # Generate OTP provisioning URI
    totp = pyotp.TOTP(user.otp_secret)
    provisioning_url = totp.provisioning_uri(
        name=user.username, 
        issuer_name="Flask QR Auth"
    )
    
    # Generate QR code
    qr_code = generate_qr_code(provisioning_url)
    
    return render_template('setup_2fa.html', user=user, qr_code=qr_code, secret=user.otp_secret)


@app.route('/verify-2fa/<int:user_id>', methods=['POST'])
def verify_2fa(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))
    
    otp_code = request.form.get('otp_code')
    totp = pyotp.TOTP(user.otp_secret)
    
    if totp.verify(otp_code):
        user.otp_enabled = True
        db.session.commit()
        flash('2FA setup successful! You can now login.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Invalid OTP code. Please try again.', 'danger')
        return redirect(url_for('setup_2fa', user_id=user.id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            if user.otp_enabled:
                # Store user ID in session and redirect to 2FA verification
                session['user_id_for_2fa'] = user.id
                return redirect(url_for('verify_login'))
            else:
                # If 2FA is not enabled, log in directly
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/verify-login', methods=['GET', 'POST'])
def verify_login():
    user_id = session.get('user_id_for_2fa')
    if not user_id:
        flash('Authentication error', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        totp = pyotp.TOTP(user.otp_secret)
        
        if totp.verify(otp_code):
            login_user(user)
            session.pop('user_id_for_2fa', None)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid OTP code. Please try again.', 'danger')
    
    return render_template('verify_login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


# Initialize the database with a command
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized.")


if __name__ == '__main__':
    # Create database tables before running the app
    with app.app_context():
        db.create_all()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=False)