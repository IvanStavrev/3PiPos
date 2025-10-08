from flask import Blueprint, render_template, request, jsonify, session
from app.models.category import Category

categories_bp = Blueprint('categories', __name__, url_prefix='/admin')

@categories_bp.before_request
def require_admin_login():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

@categories_bp.route('/categories')
def categories_list():
    categories = Category.get_all()
    return render_template('admin/categories.html', categories=categories, user_name=session.get('user_name'))

@categories_bp.route('/categories/create', methods=['POST'])
def create_category():
    try:
        category_name = request.form.get('category_name', '').strip()
        
        # Server-side validation
        if not category_name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        category = Category(
            category_name=category_name
        )
        category_id = category.create()
        return jsonify({'success': True, 'message': 'Category created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@categories_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if request.method == 'GET':
        # Return category data for editing
        category = Category.get_by_id(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'})
        
        return jsonify({
            'id': category.id,
            'category_name': category.category_name
        })
    
    elif request.method == 'POST':
        # Update category
        category = Category.get_by_id(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'})
        
        try:
            category_name = request.form.get('category_name', '').strip()
            
            # Server-side validation
            if not category_name:
                return jsonify({'success': False, 'message': 'Category name is required'})
            
            category.category_name = category_name
            category.update()
            return jsonify({'success': True, 'message': 'Category updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@categories_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    try:
        success = Category.delete(category_id)
        if success:
            return jsonify({'success': True, 'message': 'Category deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Category not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})