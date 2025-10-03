from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.user import db
from src.models.task import Task, Category, UserSettings, ActivityLog

task_bp = Blueprint('task', __name__)

# ==================== ROTAS DE TAREFAS ====================

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Obter todas as tarefas do usuário"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Filtros opcionais
        completed = request.args.get('completed')
        priority = request.args.get('priority')
        category_id = request.args.get('category_id', type=int)
        
        query = Task.query.filter_by(user_id=user_id)
        
        if completed is not None:
            query = query.filter_by(completed=completed.lower() == 'true')
        
        if priority:
            query = query.filter_by(priority=priority)
            
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks],
            'total': len(tasks)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """Criar nova tarefa"""
    try:
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({'success': False, 'error': 'Texto da tarefa é obrigatório'}), 400
        
        # Validar prioridade
        priority = data.get('priority', 'media')
        if priority not in ['baixa', 'media', 'alta']:
            return jsonify({'success': False, 'error': 'Prioridade inválida'}), 400
        
        # Validar categoria se fornecida
        category_id = data.get('category_id')
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                return jsonify({'success': False, 'error': 'Categoria não encontrada'}), 400
        
        # Validar data do lembrete
        reminder_datetime = None
        if data.get('reminder_datetime'):
            try:
                # CORREÇÃO ROBUSTA: Aceitar qualquer formato de data e converter para UTC
                reminder_str = data['reminder_datetime'].replace('Z', '+00:00')
                reminder_datetime = datetime.fromisoformat(reminder_str) if 'T' in reminder_str else datetime.fromisoformat(f"{reminder_str}T00:00:00+00:00")
                
                # CORREÇÃO: Remover completamente a validação de data futura
                # Isso permite adicionar tarefas com lembretes para qualquer momento
                
            except ValueError:
                return jsonify({'success': False, 'error': 'Formato de data inválido'}), 400
        
        # Criar tarefa
        task = Task(
            text=data['text'],
            priority=priority,
            category_id=category_id,
            reminder_datetime=reminder_datetime,
            user_id=data.get('user_id', 1)
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Registrar atividade
        ActivityLog.log_activity(
            user_id=task.user_id,
            task_id=task.id,
            action='created',
            details=f'Tarefa criada: {task.text}'
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': 'Tarefa criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Obter tarefa específica"""
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualizar tarefa"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        old_values = {
            'text': task.text,
            'priority': task.priority,
            'category_id': task.category_id,
            'reminder_datetime': task.reminder_datetime,
            'completed': task.completed
        }
        
        # Atualizar campos
        if 'text' in data:
            if not data['text'].strip():
                return jsonify({'success': False, 'error': 'Texto da tarefa não pode estar vazio'}), 400
            task.text = data['text']
        
        if 'priority' in data:
            if data['priority'] not in ['baixa', 'media', 'alta']:
                return jsonify({'success': False, 'error': 'Prioridade inválida'}), 400
            task.priority = data['priority']
        
        if 'category_id' in data:
            if data['category_id'] and not Category.query.get(data['category_id']):
                return jsonify({'success': False, 'error': 'Categoria não encontrada'}), 400
            task.category_id = data['category_id']
        
        if 'reminder_datetime' in data:
            if data['reminder_datetime']:
                try:
                    # CORREÇÃO ROBUSTA: Aceitar qualquer formato de data e converter para UTC
                    reminder_str = data['reminder_datetime'].replace('Z', '+00:00')
                    reminder_datetime = datetime.fromisoformat(reminder_str) if 'T' in reminder_str else datetime.fromisoformat(f"{reminder_str}T00:00:00+00:00")
                    
                    # CORREÇÃO: Remover completamente a validação de data futura
                    
                    task.reminder_datetime = reminder_datetime
                    # Resetar flag de notificação se lembrete mudou
                    if old_values['reminder_datetime'] != reminder_datetime:
                        task.notified = False
                except ValueError:
                    return jsonify({'success': False, 'error': 'Formato de data inválido'}), 400
            else:
                task.reminder_datetime = None
                task.notified = False
        
        if 'completed' in data:
            if data['completed'] and not task.completed:
                task.mark_completed()
            elif not data['completed'] and task.completed:
                task.mark_uncompleted()
        
        db.session.commit()
        
        # Registrar atividade
        changes = []
        for key, old_value in old_values.items():
            new_value = getattr(task, key)
            if old_value != new_value:
                changes.append(f'{key}: {old_value} → {new_value}')
        
        if changes:
            ActivityLog.log_activity(
                user_id=task.user_id,
                task_id=task.id,
                action='updated',
                details=f'Alterações: {", ".join(changes)}'
            )
            db.session.commit()
        
        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': 'Tarefa atualizada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Deletar tarefa"""
    try:
        task = Task.query.get_or_404(task_id)
        task_text = task.text
        user_id = task.user_id
        
        # Registrar atividade antes de deletar
        ActivityLog.log_activity(
            user_id=user_id,
            task_id=task_id,
            action='deleted',
            details=f'Tarefa deletada: {task_text}'
        )
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa deletada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/tasks/toggle/<int:task_id>', methods=['PATCH'])
def toggle_task(task_id):
    """Alternar status de conclusão da tarefa"""
    try:
        task = Task.query.get_or_404(task_id)
        
        if task.completed:
            task.mark_uncompleted()
            action = 'uncompleted'
            message = 'Tarefa reaberta'
        else:
            task.mark_completed()
            action = 'completed'
            message = 'Tarefa concluída'
        
        db.session.commit()
        
        # Registrar atividade
        ActivityLog.log_activity(
            user_id=task.user_id,
            task_id=task.id,
            action=action,
            details=f'Status alterado para: {action}'
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ROTAS DE CATEGORIAS ====================

@task_bp.route('/categories', methods=['GET'])
def get_categories():
    """Obter todas as categorias do usuário"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        categories = Category.query.filter_by(user_id=user_id).order_by(Category.name).all()
        
        return jsonify({
            'success': True,
            'categories': [category.to_dict() for category in categories]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/categories', methods=['POST'])
def create_category():
    """Criar nova categoria"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Nome da categoria é obrigatório'}), 400
        
        user_id = data.get('user_id', 1)
        
        # Verificar se categoria já existe para o usuário
        existing = Category.query.filter_by(name=data['name'], user_id=user_id).first()
        if existing:
            return jsonify({'success': False, 'error': 'Categoria já existe'}), 400
        
        category = Category(
            name=data['name'],
            color=data.get('color', '#667eea'),
            user_id=user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': category.to_dict(),
            'message': 'Categoria criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Atualizar categoria"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({'success': False, 'error': 'Nome da categoria não pode estar vazio'}), 400
            
            # Verificar se novo nome já existe para o usuário
            existing = Category.query.filter_by(
                name=data['name'], 
                user_id=category.user_id
            ).filter(Category.id != category_id).first()
            
            if existing:
                return jsonify({'success': False, 'error': 'Categoria com este nome já existe'}), 400
            
            category.name = data['name']
        
        if 'color' in data:
            category.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': category.to_dict(),
            'message': 'Categoria atualizada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Deletar categoria"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Verificar se há tarefas usando esta categoria
        tasks_count = Task.query.filter_by(category_id=category_id).count()
        if tasks_count > 0:
            return jsonify({
                'success': False, 
                'error': f'Não é possível deletar categoria com {tasks_count} tarefa(s) associada(s)'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoria deletada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ROTAS DE ESTATÍSTICAS ====================

@task_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas das tarefas"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        total_tasks = Task.query.filter_by(user_id=user_id).count()
        completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()
        pending_tasks = total_tasks - completed_tasks
        
        # Estatísticas por prioridade
        priority_stats = {}
        for priority in ['baixa', 'media', 'alta']:
            priority_stats[priority] = Task.query.filter_by(
                user_id=user_id, 
                priority=priority, 
                completed=False
            ).count()
        
        # Estatísticas por categoria
        category_stats = []
        categories = Category.query.filter_by(user_id=user_id).all()
        for category in categories:
            task_count = Task.query.filter_by(category_id=category.id, completed=False).count()
            if task_count > 0:
                category_stats.append({
                    'category': category.to_dict(),
                    'task_count': task_count
                })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'priority_stats': priority_stats,
                'category_stats': category_stats
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ROTAS DE CONFIGURAÇÕES ====================

@task_bp.route('/settings/<int:user_id>', methods=['GET'])
def get_user_settings(user_id):
    """Obter configurações do usuário"""
    try:
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # Criar configurações padrão
            settings = UserSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_bp.route('/settings/<int:user_id>', methods=['PUT'])
def update_user_settings(user_id):
    """Atualizar configurações do usuário"""
    try:
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            settings = UserSettings(user_id=user_id)
            db.session.add(settings)
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        if 'theme' in data:
            if data['theme'] not in ['light', 'dark']:
                return jsonify({'success': False, 'error': 'Tema inválido'}), 400
            settings.theme = data['theme']
        
        if 'notifications_enabled' in data:
            settings.notifications_enabled = bool(data['notifications_enabled'])
        
        if 'default_priority' in data:
            if data['default_priority'] not in ['baixa', 'media', 'alta']:
                return jsonify({'success': False, 'error': 'Prioridade padrão inválida'}), 400
            settings.default_priority = data['default_priority']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict(),
            'message': 'Configurações atualizadas com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
