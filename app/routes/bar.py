from flask import Blueprint, render_template, session, redirect, url_for

bar_bp = Blueprint('bar', __name__, url_prefix='/bar')

@bar_bp.route('/orders')
def orders():
    if not session.get('logged_in') or session.get('user_role') != 'bar':
        return redirect(url_for('auth.login'))
    return render_template('bar/orders.html', user_name=session.get('user_name'))