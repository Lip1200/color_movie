from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from src.models.local import Utilisateur
from flask_login import current_user, UserMixin, LoginManager, login_user
import src.models.local.base
from dotenv import load_dotenv
import os
load_dotenv()
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

def create_admin_user(app):
    with app.app_context():
        admin_user = Utilisateur(
            nom='admin',
            email='sarah.tat@etu.unige.ch',
            is_admin=True
        )
        admin_user.set_password(os.environ.get("ADMIN_PASSWORD", ""))
        db.session.add(admin_user)
        db.session.commit()

def setup_admin(app):
    admin.init_app(app)
    admin.add_view(AdminModelView(Utilisateur, db.session))
