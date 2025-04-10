from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import FixedScheduleItem, Task, ScheduledBlock

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page / Dashboard"""
    if current_user.is_authenticated:
        # Get statistics for the dashboard
        fixed_schedule_count = FixedScheduleItem.query.filter_by(user_id=current_user.id).count()
        pending_tasks_count = Task.query.filter_by(user_id=current_user.id, status='pending').count()
        scheduled_tasks_count = Task.query.filter_by(user_id=current_user.id, status='scheduled').count()
        completed_tasks_count = Task.query.filter_by(user_id=current_user.id, status='completed').count()
        
        # Get upcoming schedule items and tasks
        upcoming_schedule = FixedScheduleItem.query.filter_by(user_id=current_user.id).order_by(FixedScheduleItem.start_time).limit(5).all()
        upcoming_tasks = Task.query.filter_by(user_id=current_user.id, status='scheduled').order_by(Task.deadline).limit(5).all()
        
        return render_template('dashboard.html', 
                              fixed_schedule_count=fixed_schedule_count,
                              pending_tasks_count=pending_tasks_count,
                              scheduled_tasks_count=scheduled_tasks_count,
                              completed_tasks_count=completed_tasks_count,
                              upcoming_schedule=upcoming_schedule,
                              upcoming_tasks=upcoming_tasks)
    else:
        return render_template('landing.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return redirect(url_for('main.index'))
