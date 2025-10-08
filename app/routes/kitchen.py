from flask import Blueprint, render_template, session, redirect, url_for

kitchen_bp = Blueprint('kitchen', __name__, url_prefix='/kitchen')

@kitchen_bp.route('/orders')
def orders():
    if not session.get('logged_in') or session.get('user_role') != 'kitchen':
        return redirect(url_for('auth.login'))
    return render_template('kitchen/orders.html', user_name=session.get('user_name'))