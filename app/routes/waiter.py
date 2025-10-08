from flask import Blueprint, render_template, session, redirect, url_for

waiter_bp = Blueprint('waiter', __name__, url_prefix='/waiter')

@waiter_bp.route('/orders')
def orders():
    if not session.get('logged_in') or session.get('user_role') != 'waiter':
        return redirect(url_for('auth.login'))
    return render_template('waiter/orders.html', user_name=session.get('user_name'))