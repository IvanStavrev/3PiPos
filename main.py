from flask import Flask, render_template, redirect, url_for, session, request
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.waiter import waiter_bp
from app.routes.bar import bar_bp
from app.routes.kitchen import kitchen_bp
from app.routes.tables import tables_bp
from app.routes.categories import categories_bp
from app.translations import translations

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

# Translation helper 
def translate(key, *args):
    lang = session.get('language', 'en')
    # Get the translation dictionary for the language, fallback to English
    lang_dict = translations.get(lang, translations['en'])
    # Get the text, fallback to the key if not found
    text = lang_dict.get(key, key)
    return text.format(*args) if args else text

# Make it available to all templates
@app.context_processor
def utility_processor():
    return dict(translate=translate)

# Language setting route
@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'bg']:
        session['language'] = lang
    # Redirect back to the previous page
    return redirect(request.referrer or url_for('index'))

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(waiter_bp)
app.register_blueprint(bar_bp)
app.register_blueprint(kitchen_bp)
app.register_blueprint(tables_bp)
app.register_blueprint(categories_bp)

@app.route('/')
def index():
    if session.get('logged_in'):
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin.users_list'))
        elif role == 'waiter':
            return redirect(url_for('waiter.orders'))
        elif role == 'bar':
            return redirect(url_for('bar.orders'))
        elif role == 'kitchen':
            return redirect(url_for('kitchen.orders'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)