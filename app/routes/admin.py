from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin_login():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        return redirect(url_for('auth.login'))

@admin_bp.route('/users')
def users_list():
    users = User.get_all()
    return render_template('admin/users.html', users=users, user_name=session.get('user_name'))

# ... rest of your admin routes remain the same ...
@admin_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        try:
            user = User(
                name=request.form['name'],
                familyname=request.form['familyname'],
                phone=request.form['phone'],
                password=request.form['password'],
                role=request.form['role']
            )
            user_id = user.create()
            return jsonify({'success': True, 'message': 'User created successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('admin/user_form.html', user=None)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.familyname = request.form['familyname']
            user.phone = request.form['phone']
            user.role = request.form['role']
            
            if request.form.get('password'):
                user.password = request.form['password']
            
            user.update()
            return jsonify({'success': True, 'message': 'User updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'familyname': user.familyname,
        'phone': user.phone,
        'role': user.role
    })

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        success = User.delete(user_id)
        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})