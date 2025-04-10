from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.forms import FixedScheduleItemForm
from app.models.models import FixedScheduleItem
from app import db
from datetime import datetime

schedule = Blueprint('schedule', __name__)

@schedule.route('/')
@login_required
def index():
    """Display the user's schedule"""
    schedule_items = FixedScheduleItem.query.filter_by(user_id=current_user.id).all()
    return render_template('schedule/index.html', schedule_items=schedule_items)

@schedule.route('/view')
@login_required
def view():
    """View the intelligent schedule with fixed items and scheduled tasks"""
    from app.models.models import ScheduledBlock
    
    fixed_schedule = FixedScheduleItem.query.filter_by(user_id=current_user.id).all()
    scheduled_blocks = ScheduledBlock.query.filter_by(user_id=current_user.id).all()
    
    # Get the associated tasks for each scheduled block
    for block in scheduled_blocks:
        block.task = Task.query.get(block.task_id)
    
    return render_template('schedule/view.html', 
                          fixed_schedule=fixed_schedule,
                          scheduled_blocks=scheduled_blocks)

@schedule.route('/new', methods=['GET', 'POST'])
@login_required
def new_schedule_item():
    """Create a new fixed schedule item"""
    form = FixedScheduleItemForm()
    if form.validate_on_submit():
        schedule_item = FixedScheduleItem(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            recurrence_pattern=form.recurrence_pattern.data,
            recurrence_end_date=form.recurrence_end_date.data,
            priority=form.priority.data,
            category=form.category.data,
            color=form.color.data
        )
        db.session.add(schedule_item)
        db.session.commit()
        flash('Schedule item added successfully!', 'success')
        return redirect(url_for('schedule.index'))
    return render_template('schedule/new.html', form=form)

@schedule.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_schedule_item(id):
    """Edit an existing fixed schedule item"""
    schedule_item = FixedScheduleItem.query.get_or_404(id)
    # Check if the schedule item belongs to the current user
    if schedule_item.user_id != current_user.id:
        flash('You do not have permission to edit this schedule item.', 'danger')
        return redirect(url_for('schedule.index'))
    
    form = FixedScheduleItemForm(obj=schedule_item)
    if form.validate_on_submit():
        schedule_item.title = form.title.data
        schedule_item.description = form.description.data
        schedule_item.start_time = form.start_time.data
        schedule_item.end_time = form.end_time.data
        schedule_item.recurrence_pattern = form.recurrence_pattern.data
        schedule_item.recurrence_end_date = form.recurrence_end_date.data
        schedule_item.priority = form.priority.data
        schedule_item.category = form.category.data
        schedule_item.color = form.color.data
        
        db.session.commit()
        flash('Schedule item updated successfully!', 'success')
        return redirect(url_for('schedule.index'))
    
    return render_template('schedule/edit.html', form=form, schedule_item=schedule_item)

@schedule.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_schedule_item(id):
    """Delete a fixed schedule item"""
    schedule_item = FixedScheduleItem.query.get_or_404(id)
    # Check if the schedule item belongs to the current user
    if schedule_item.user_id != current_user.id:
        flash('You do not have permission to delete this schedule item.', 'danger')
        return redirect(url_for('schedule.index'))
    
    db.session.delete(schedule_item)
    db.session.commit()
    flash('Schedule item deleted successfully!', 'success')
    return redirect(url_for('schedule.index'))

@schedule.route('/api/items', methods=['GET'])
@login_required
def get_schedule_items():
    """API endpoint to get all schedule items for the current user"""
    schedule_items = FixedScheduleItem.query.filter_by(user_id=current_user.id).all()
    items = []
    for item in schedule_items:
        # Handle recurring events
        if item.recurrence_pattern == 'none':
            items.append({
                'id': item.id,
                'title': item.title,
                'start': item.start_time.isoformat(),
                'end': item.end_time.isoformat(),
                'color': item.color,
                'extendedProps': {
                    'description': item.description,
                    'category': item.category,
                    'priority': item.priority
                }
            })
        else:
            # For recurring events, we'll handle them client-side with FullCalendar's recurrence plugin
            items.append({
                'id': item.id,
                'title': item.title,
                'startTime': item.start_time.strftime('%H:%M'),
                'endTime': item.end_time.strftime('%H:%M'),
                'startRecur': item.start_time.date().isoformat(),
                'endRecur': item.recurrence_end_date.isoformat() if item.recurrence_end_date else None,
                'daysOfWeek': [item.start_time.weekday()] if item.recurrence_pattern == 'weekly' else None,
                'color': item.color,
                'extendedProps': {
                    'description': item.description,
                    'category': item.category,
                    'priority': item.priority,
                    'recurrence': item.recurrence_pattern
                }
            })
    
    return jsonify(items)
