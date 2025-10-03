from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#667eea')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tasks = db.relationship('Task', backref='category', lazy=True, cascade='all, delete-orphan')
    
    # Constraint única para nome por usuário
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_category_per_user'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), default='media')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    reminder_datetime = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    activity_logs = db.relationship('ActivityLog', backref='task', lazy=True, cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("priority IN ('baixa', 'media', 'alta')", name='check_priority'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'priority': self.priority,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'reminder_datetime': self.reminder_datetime.isoformat() if self.reminder_datetime else None,
            'completed': self.completed,
            'notified': self.notified,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def mark_completed(self):
        """Marca a tarefa como concluída e define completed_at"""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def mark_uncompleted(self):
        """Marca a tarefa como não concluída e limpa completed_at"""
        self.completed = False
        self.completed_at = None

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    theme = db.Column(db.String(10), default='light')
    notifications_enabled = db.Column(db.Boolean, default=True)
    default_priority = db.Column(db.String(10), default='media')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("theme IN ('light', 'dark')", name='check_theme'),
        db.CheckConstraint("default_priority IN ('baixa', 'media', 'alta')", name='check_default_priority'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'notifications_enabled': self.notifications_enabled,
            'default_priority': self.default_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # 'created', 'updated', 'completed', 'deleted'
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'action': self.action,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def log_activity(user_id, action, task_id=None, details=None):
        """Método utilitário para registrar atividades"""
        log = ActivityLog(
            user_id=user_id,
            task_id=task_id,
            action=action,
            details=details
        )
        db.session.add(log)
        return log
