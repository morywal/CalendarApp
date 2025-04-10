from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Relationships
    fixed_schedule_items = db.relationship('FixedScheduleItem', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    scheduled_blocks = db.relationship('ScheduledBlock', backref='user', lazy='dynamic')
    preferences = db.relationship('UserPreferences', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_day_time = db.Column(db.Time, default=datetime.strptime('08:00', '%H:%M').time())
    end_day_time = db.Column(db.Time, default=datetime.strptime('22:00', '%H:%M').time())
    min_break_duration = db.Column(db.Integer, default=15)  # minutes
    preferred_task_duration = db.Column(db.Integer, default=60)  # minutes
    productivity_factors = db.Column(db.JSON, default={})
    
    def __repr__(self):
        return f'<UserPreferences for User {self.user_id}>'

class FixedScheduleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    recurrence_pattern = db.Column(db.String(20), default='none')  # none, daily, weekly, monthly
    recurrence_end_date = db.Column(db.Date)
    priority = db.Column(db.Integer, default=3)  # 1-5
    category = db.Column(db.String(50))
    color = db.Column(db.String(20), default='#3788d8')
    
    def __repr__(self):
        return f'<FixedScheduleItem {self.title}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    deadline = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer)  # minutes
    actual_duration = db.Column(db.Integer)  # minutes
    priority = db.Column(db.Integer, default=3)  # 1-5
    status = db.Column(db.String(20), default='pending')  # pending, scheduled, in_progress, completed
    category = db.Column(db.String(50))
    
    # Relationships
    scheduled_blocks = db.relationship('ScheduledBlock', backref='task', lazy='dynamic')
    
    def __repr__(self):
        return f'<Task {self.title}>'

class TaskDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    dependent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    
    # Relationships
    task = db.relationship('Task', foreign_keys=[task_id], backref=db.backref('dependencies', lazy='dynamic'))
    dependent_task = db.relationship('Task', foreign_keys=[dependent_task_id], backref=db.backref('dependents', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TaskDependency {self.task_id} -> {self.dependent_task_id}>'

class ScheduledBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='suggested')  # suggested, confirmed, completed
    
    def __repr__(self):
        return f'<ScheduledBlock for Task {self.task_id}>'
