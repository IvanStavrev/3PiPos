from flask import Blueprint, render_template, request, jsonify, session
from app.models.table import Table

tables_bp = Blueprint('tables', __name__, url_prefix='/admin')

@tables_bp.before_request
def require_admin_login():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

@tables_bp.route('/tables')
def tables_list():
    tables = Table.get_all()
    return render_template('admin/tables.html', tables=tables, user_name=session.get('user_name'))

@tables_bp.route('/tables/create', methods=['POST'])
def create_table():
    try:
        table = Table(
            table_name=request.form['table_name'],
            table_seats=int(request.form['table_seats']),
            table_status=request.form.get('table_status', 'free'),
            table_reservationnote=request.form.get('table_reservationnote', '')
        )
        table_id = table.create()
        return jsonify({'success': True, 'message': 'Table created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tables_bp.route('/tables/edit/<int:table_id>', methods=['GET', 'POST'])
def edit_table(table_id):
    table = Table.get_by_id(table_id)
    if not table:
        return jsonify({'success': False, 'message': 'Table not found'})
    
    if request.method == 'POST':
        try:
            table.table_name = request.form['table_name']
            table.table_seats = int(request.form['table_seats'])
            table.table_status = request.form['table_status']
            table.table_reservationnote = request.form.get('table_reservationnote', '')
            
            table.update()
            return jsonify({'success': True, 'message': 'Table updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({
        'id': table.id,
        'table_name': table.table_name,
        'table_seats': table.table_seats,
        'table_status': table.table_status,
        'table_reservationnote': table.table_reservationnote or ''
    })

@tables_bp.route('/tables/delete/<int:table_id>', methods=['POST'])
def delete_table(table_id):
    try:
        success = Table.delete(table_id)
        if success:
            return jsonify({'success': True, 'message': 'Table deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Table not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tables_bp.route('/tables/reserve/<int:table_id>', methods=['POST'])
def reserve_table(table_id):
    try:
        note = request.form.get('note', '').strip()
        
        # Server-side validation
        if not note:
            return jsonify({'success': False, 'message': 'Reservation note is required'})
        
        table = Table.get_by_id(table_id)
        if table:
            user_id = session.get('user_id')
            table.reserve(user_id, note)
            return jsonify({'success': True, 'message': 'Table reserved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Table not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tables_bp.route('/tables/free/<int:table_id>', methods=['POST'])
def free_table(table_id):
    try:
        table = Table.get_by_id(table_id)
        if table:
            user_id = session.get('user_id')
            table.free(user_id)
            return jsonify({'success': True, 'message': 'Table freed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Table not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})