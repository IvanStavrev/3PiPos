from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.user import User
from werkzeug.security import generate_password_hash
import re

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin_login():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        return redirect(url_for('auth.login'))

@admin_bp.route('/users')
def users_list():
    users = User.get_all()
    return render_template('admin/users.html', users=users, user_name=session.get('user_name'))

@admin_bp.route('/users/test-db', methods=['GET'])
def test_db():
    """Test database connection and basic operations"""
    try:
        from app.config.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test 1: Check if we can query the database
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Database connection successful. Found {result["count"]} users.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database connection failed: {str(e)}'
        }), 500

@admin_bp.route('/users/debug-data', methods=['GET'])
def debug_users_data():
    """Debug route to see raw user data"""
    try:
        from app.config.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get raw data from database
        cursor.execute("SELECT user_id, name, familyname, phone, role FROM users")
        raw_users = cursor.fetchall()
        
        # Get data through User model
        users_from_model = User.get_all()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'raw_database_data': raw_users,
            'users_from_model': [user.__dict__ for user in users_from_model]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/users/create', methods=['POST'])
def create_user():
    try:
        # Get and sanitize form data
        name = request.form.get('name', '').strip()
        family_name = request.form.get('family_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()

        print(f"=== CREATE USER DEBUG ===")
        print(f"Name: {name}")
        print(f"Family Name: {family_name}")
        print(f"Phone: {phone}")
        print(f"Password: {'*' * len(password) if password else 'None'}")
        print(f"Role: {role}")
        print(f"=======================")

        # Validate required fields
        if not all([name, family_name, phone, password, role]):
            return jsonify({
                'success': False, 
                'message': 'All fields are required',
                'errors': ['Please fill in all required fields']
            }), 400

        # Name validation - UPDATED FOR CYRILLIC
        if len(name) < 2 or len(name) > 50:
            return jsonify({
                'success': False,
                'message': 'Invalid name',
                'errors': ['Name must be between 2 and 50 characters']
            }), 400

        # Updated regex for Cyrillic support
        if not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', name):
            return jsonify({
                'success': False,
                'message': 'Invalid name format',
                'errors': ['Name can only contain letters and spaces']
            }), 400

        # Family name validation - UPDATED FOR CYRILLIC
        if len(family_name) < 2 or len(family_name) > 50:
            return jsonify({
                'success': False,
                'message': 'Invalid family name',
                'errors': ['Family name must be between 2 and 50 characters']
            }), 400

        # Updated regex for Cyrillic support
        if not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', family_name):
            return jsonify({
                'success': False,
                'message': 'Invalid family name format',
                'errors': ['Family name can only contain letters and spaces']
            }), 400

        # Phone validation
        if not re.match(r'^\+?[0-9\s\-\(\)]{10,}$', phone):
            return jsonify({
                'success': False,
                'message': 'Invalid phone number',
                'errors': ['Please enter a valid phone number (minimum 10 digits)']
            }), 400

        # Check if phone already exists
        if not User.is_phone_unique(phone):
            return jsonify({
                'success': False,
                'message': 'Phone number exists',
                'errors': ['Phone number already registered with another user']
            }), 400

        # Password validation
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Weak password',
                'errors': ['Password must be at least 6 characters long']
            }), 400

        # Role validation
        valid_roles = ['admin', 'waiter', 'bar', 'kitchen']
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'message': 'Invalid role',
                'errors': ['Please select a valid role']
            }), 400

        # Create user - FIXED: Use User.create_user with plain password (it will hash it)
        user_id = User.create_user(
            name=name,
            family_name=family_name,
            phone=phone,
            password=password,  # Pass plain password, let User model hash it
            role=role
        )

        if user_id:
            return jsonify({
                'success': True, 
                'message': 'User created successfully',
                'user_id': user_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create user',
                'errors': ['Database error: Could not create user']
            }), 500

    except KeyError as e:
        return jsonify({
            'success': False,
            'message': 'Missing form data',
            'errors': [f'Missing required field: {str(e)}']
        }), 400
    except Exception as e:
        print(f"=== SERVER ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()  # This will show the full traceback
        print(f"===================")
        return jsonify({
            'success': False,
            'message': 'Server error',
            'errors': [f'An unexpected error occurred: {str(e)}'],
            'debug_info': str(e)  # Include actual error for debugging
        }), 500

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    try:
        if request.method == 'GET':
            # Get user data for editing - FIXED: Use correct attribute names
            user = User.get_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            return jsonify({
                'success': True,
                'user': {
                    'id': user.user_id,  # FIXED: Use user_id instead of id
                    'name': user.name,
                    'family_name': user.familyname,  # FIXED: Use familyname instead of family_name
                    'phone': user.phone,
                    'role': user.role
                }
            })

        elif request.method == 'POST':
            # Update user data
            name = request.form.get('name', '').strip()
            family_name = request.form.get('family_name', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', '').strip()

            # Validate required fields (except password)
            if not all([name, family_name, phone, role]):
                return jsonify({
                    'success': False, 
                    'message': 'Missing required fields',
                    'errors': ['Name, family name, phone, and role are required']
                }), 400

            # Name validation
            if len(name) < 2 or len(name) > 50:
                return jsonify({
                    'success': False,
                    'message': 'Invalid name',
                    'errors': ['Name must be between 2 and 50 characters']
                }), 400

            if not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', name):
                return jsonify({
                    'success': False,
                    'message': 'Invalid name format',
                    'errors': ['Name can only contain letters and spaces']
                }), 400

            # Family name validation
            if len(family_name) < 2 or len(family_name) > 50:
                return jsonify({
                    'success': False,
                    'message': 'Invalid family name',
                    'errors': ['Family name must be between 2 and 50 characters']
                }), 400

            if not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', family_name):
                return jsonify({
                    'success': False,
                    'message': 'Invalid family name format',
                    'errors': ['Family name can only contain letters and spaces']
                }), 400

            # Phone validation
            if not re.match(r'^\+?[0-9\s\-\(\)]{10,}$', phone):
                return jsonify({
                    'success': False,
                    'message': 'Invalid phone number',
                    'errors': ['Please enter a valid phone number (minimum 10 digits)']
                }), 400

            # Check if phone already exists (excluding current user)
            if not User.is_phone_unique(phone, exclude_user_id=user_id):
                return jsonify({
                    'success': False,
                    'message': 'Phone number exists',
                    'errors': ['Phone number already registered with another user']
                }), 400

            # Password validation (only if provided)
            if password and len(password) < 6:
                return jsonify({
                    'success': False,
                    'message': 'Weak password',
                    'errors': ['Password must be at least 6 characters long']
                }), 400

            # Role validation
            valid_roles = ['admin', 'waiter', 'bar', 'kitchen']
            if role not in valid_roles:
                return jsonify({
                    'success': False,
                    'message': 'Invalid role',
                    'errors': ['Please select a valid role']
                }), 400

            # Update user - FIXED: Use User.update_user with plain password
            update_data = {
                'name': name,
                'family_name': family_name,
                'phone': phone,
                'role': role
            }

            # Only update password if provided
            if password:
                update_data['password'] = password  # Pass plain password, let User model hash it

            success = User.update_user(user_id, update_data)

            if success:
                return jsonify({
                    'success': True, 
                    'message': 'User updated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update user',
                    'errors': ['User not found or database error']
                }), 500

    except Exception as e:
        print(f"=== EDIT USER ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=====================")
        return jsonify({
            'success': False,
            'message': 'Server error',
            'errors': [f'An unexpected error occurred: {str(e)}'],
            'debug_info': str(e)  # Include actual error for debugging
        }), 500

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        # Prevent self-deletion
        if session.get('user_id') == user_id:
            return jsonify({
                'success': False,
                'message': 'Cannot delete own account',
                'errors': ['You cannot delete your own user account']
            }), 400

        success = User.delete_user(user_id)
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'User deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['The user you are trying to delete does not exist']
            }), 404

    except Exception as e:
        print(f"=== DELETE USER ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=======================")
        return jsonify({
            'success': False,
            'message': 'Server error',
            'errors': [f'An unexpected error occurred: {str(e)}'],
            'debug_info': str(e)  # Include actual error for debugging
        }), 500