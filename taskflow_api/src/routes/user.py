from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, db
from src.models.task import UserSettings

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Obter todos os usuários (apenas para fins administrativos)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Registrar novo usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False, 
                'error': 'Nome de usuário, email e senha são obrigatórios'
            }), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Nome de usuário já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email já está em uso'}), 400
        
        # Criar usuário
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Criar configurações padrão para o usuário
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Usuário criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obter usuário específico"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualizar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        # Atualizar campos
        if 'username' in data:
            if not data['username'].strip():
                return jsonify({'success': False, 'error': 'Nome de usuário não pode estar vazio'}), 400
            
            # Verificar se novo nome já existe
            existing = User.query.filter_by(username=data['username']).filter(User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Nome de usuário já existe'}), 400
            
            user.username = data['username']
        
        if 'email' in data:
            if not data['email'].strip():
                return jsonify({'success': False, 'error': 'Email não pode estar vazio'}), 400
            
            # Verificar se novo email já existe
            existing = User.query.filter_by(email=data['email']).filter(User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Email já está em uso'}), 400
            
            user.email = data['email']
        
        if 'password' in data:
            if not data['password'] or len(data['password']) < 6:
                return jsonify({'success': False, 'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
            
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Usuário atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Não permitir deletar o usuário padrão
        if user_id == 1:
            return jsonify({'success': False, 'error': 'Não é possível deletar o usuário padrão'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário deletado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Nome de usuário e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Login realizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
