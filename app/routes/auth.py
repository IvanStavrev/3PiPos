from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        print(f"Login attempt with password: {password}")  # Debug
        
        user = User.authenticate_by_password(password)
        print(f"User found: {user}")  # Debug
        
        if user:
            session['user_id'] = user.user_id
            session['user_name'] = f"{user.name} {user.familyname}"
            session['user_role'] = user.role
            session['logged_in'] = True
            
            print(f"User authenticated: {user.name}, Role: {user.role}")  # Debug
            
            # For AJAX requests, return JSON to indicate success
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Login successful'})
            
            # For form submission, redirect directly
            if user.role == 'admin':
                return redirect(url_for('admin.users_list'))
            elif user.role == 'waiter':
                return redirect(url_for('waiter.orders'))
            elif user.role == 'bar':
                return redirect(url_for('bar.orders'))
            elif user.role == 'kitchen':
                return redirect(url_for('kitchen.orders'))
        else:
            print("Authentication failed")  # Debug
            return jsonify({'success': False, 'message': 'Invalid password'})
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))