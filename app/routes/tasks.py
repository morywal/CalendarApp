from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import Task
from app.models.duration_estimator import suggest_task_duration, get_duration_estimator
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

tasks = Blueprint('tasks', __name__)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    deadline = DateTimeField('Deadline', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    estimated_duration = IntegerField('Estimated Duration (minutes)', validators=[Optional(), NumberRange(min=1)])
    priority = SelectField('Priority', choices=[
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High')
    ], default='3', coerce=int)
    category = StringField('Category', validators=[Optional(), Length(max=50)])

@tasks.route('/')
@login_required
def index():
    """Display the user's tasks"""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks/index.html', tasks=tasks)

@tasks.route('/new', methods=['GET', 'POST'])
@login_required
def new_task():
    """Create a new task"""
    form = TaskForm()
    if form.validate_on_submit():
        # Get the estimated duration from the form or suggest one
        estimated_duration = form.estimated_duration.data
        if not estimated_duration:
            # If user didn't provide an estimate, suggest one based on task type
            estimated_duration = suggest_task_duration(
                form.title.data, 
                form.description.data, 
                form.category.data,
                user_id=current_user.id
            )
        
        task = Task(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            estimated_duration=estimated_duration,
            priority=form.priority.data,
            category=form.category.data,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.index'))
    return render_template('tasks/new.html', form=form)

@tasks.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    """Edit an existing task"""
    task = Task.query.get_or_404(id)
    # Check if the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('tasks.index'))
    
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.estimated_duration = form.estimated_duration.data or suggest_task_duration(
            form.title.data, 
            form.description.data, 
            form.category.data,
            user_id=current_user.id
        )
        task.priority = form.priority.data
        task.category = form.category.data
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/edit.html', form=form, task=task)

@tasks.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    """Delete a task"""
    task = Task.query.get_or_404(id)
    # Check if the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('tasks.index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.index'))

@tasks.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    """Update task status"""
    task = Task.query.get_or_404(id)
    # Check if the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('tasks.index'))
    
    status = request.form.get('status')
    if status in ['pending', 'scheduled', 'in_progress', 'completed']:
        # If task is being marked as completed, record the completion time
        if status == 'completed' and task.status != 'completed':
            # In a real app, we would record the actual completion time
            # For now, we'll just mark it as completed
            pass
            
        task.status = status
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('tasks.index'))

@tasks.route('/update_actual_duration/<int:id>', methods=['POST'])
@login_required
def update_actual_duration(id):
    """Update the actual duration of a completed task"""
    task = Task.query.get_or_404(id)
    # Check if the task belongs to the current user
    if task.user_id != current_user.id:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('tasks.index'))
    
    actual_duration = request.form.get('actual_duration')
    if actual_duration and actual_duration.isdigit():
        task.actual_duration = int(actual_duration)
        db.session.commit()
        
        # Update the duration estimation model with this feedback
        estimator = get_duration_estimator(current_user.id)
        estimator.update_model_with_feedback(current_user.id)
        
        flash('Task duration feedback recorded. Thank you!', 'success')
    else:
        flash('Invalid duration value.', 'danger')
    
    return redirect(url_for('tasks.edit_task', id=id))

@tasks.route('/generate_schedule')
@login_required
def generate_schedule():
    """Generate a schedule for pending tasks"""
    from app.models.scheduler import schedule_tasks_for_user
    
    # Clear any existing scheduled blocks
    from app.models.models import ScheduledBlock
    ScheduledBlock.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    # Generate new schedule
    scheduled_blocks = schedule_tasks_for_user(current_user.id)
    
    if scheduled_blocks:
        flash(f'Successfully scheduled {len(scheduled_blocks)} tasks!', 'success')
    else:
        flash('No tasks were scheduled. Add some pending tasks first.', 'info')
    
    return redirect(url_for('tasks.index'))

@tasks.route('/api/estimate_duration', methods=['POST'])
@login_required
def api_estimate_duration():
    """API endpoint to estimate task duration"""
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    category = data.get('category', '')
    
    estimated_duration = suggest_task_duration(
        title, 
        description, 
        category,
        user_id=current_user.id
    )
    
    return jsonify({'estimated_duration': estimated_duration})
