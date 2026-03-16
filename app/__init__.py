# app/__init__.py
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Load configuration from config.py
    app.config.from_object(Config)

    # Create upload folder if it doesn't exist (after config is loaded)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configurazione Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Devi effettuare il login per accedere a questa pagina.'
    login_manager.login_message_category = 'info'

    # Blueprints
    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    from .blueprints.admin.routes_main import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")
    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from .blueprints.dati import bp as dati_bp
    app.register_blueprint(dati_bp, url_prefix="/dati")
    from .blueprints.stats import stats_bp, stats_general_bp
    app.register_blueprint(stats_bp)
    app.register_blueprint(stats_general_bp)
    from .blueprints.help import help_bp
    app.register_blueprint(help_bp)
    from .blueprints.agent import agent_bp
    app.register_blueprint(agent_bp, url_prefix="/agent")


    # Import modelli se presenti
    try:
        from . import models  # noqa: F401
    except Exception:
        pass

    # User loader per Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # LOG diagnostico (utile solo ora)
    print("instance_path:", app.instance_path)
    print("SQLALCHEMY_DATABASE_URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
