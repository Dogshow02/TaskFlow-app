import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db, User
from src.models.task import Category, Task, UserSettings, ActivityLog
from src.routes.user import user_bp
from src.routes.task import task_bp
from src.routes.frontend import frontend_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app)  # Habilitar CORS para todas as rotas

# Configuração
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'taskflow.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False  # Manter ordem das chaves em JSON

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')
app.register_blueprint(frontend_bp)

# Inicializar banco de dados
db.init_app(app)

# Criar tabelas e dados iniciais
with app.app_context():
    db.create_all()
    
    # Criar usuário padrão se não existir
    if not User.query.filter_by(id=1).first():
        default_user = User(
            id=1,
            username='default',
            email='default@taskflow.com',
            password_hash='pbkdf2:sha256:150000$ImTyXAJY$b06a1fd31e5c336a177e4404b4cb1a2001f7c8ef7be8eea3498f53d078f3fd4a'  # senha: default
        )
        db.session.add(default_user)
        db.session.commit()
    
    # Criar configurações padrão se não existirem
    if not UserSettings.query.filter_by(user_id=1).first():
        default_settings = UserSettings(user_id=1)
        db.session.add(default_settings)
        db.session.commit()
    
    # Criar categorias padrão se não existirem
    default_categories = [
        {'name': 'Trabalho', 'color': '#667eea'},
        {'name': 'Pessoal', 'color': '#4caf50'},
        {'name': 'Estudos', 'color': '#ff9800'},
        {'name': 'Saúde', 'color': '#e74c3c'},
        {'name': 'Compras', 'color': '#9c27b0'}
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data['name'], user_id=1).first():
            category = Category(
                name=cat_data['name'],
                color=cat_data['color'],
                user_id=1
            )
            db.session.add(category)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
