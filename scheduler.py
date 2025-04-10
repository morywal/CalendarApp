import datetime
import numpy as np
from app.models.models import FixedScheduleItem, Task, ScheduledBlock
from app import db
from flask_login import current_user

class IntelligentScheduler:
    """
    Intelligent scheduling algorithm that finds optimal time blocks
    for tasks based on fixed schedule, task properties, and user preferences.
    """
    
    def __init__(self, user_id, start_date=None, end_date=None, min_block_duration=15):
        """
        Initialize the scheduler with user-specific parameters.
        
        Args:
            user_id: ID of the user to generate schedule for
            start_date: Start date for scheduling (defaults to today)
            end_date: End date for scheduling (defaults to 7 days from start)
            min_block_duration: Minimum duration (in minutes) for a free time block
        """
        self.user_id = user_id
        self.start_date = start_date or datetime.datetime.now().date()
        self.end_date = end_date or (self.start_date + datetime.timedelta(days=7))
        self.min_block_duration = min_block_duration
        
        # Get user preferences (default values if not set)
        self.start_day_time = datetime.time(8, 0)  # 8:00 AM
        self.end_day_time = datetime.time(22, 0)   # 10:00 PM
        
        # Load user preferences if available
        from app.models.models import UserPreferences
        user_prefs = UserPreferences.query.filter_by(user_id=user_id).first()
        if user_prefs:
            self.start_day_time = user_prefs.start_day_time
            self.end_day_time = user_prefs.end_day_time
            self.min_block_duration = user_prefs.min_break_duration
    
    def get_fixed_schedule_items(self):
        """Get all fixed schedule items for the user within the date range."""
        # Get base items
        items = FixedScheduleItem.query.filter_by(user_id=self.user_id).all()
        
        # Expand recurring items
        expanded_items = []
        
        for item in items:
            # For non-recurring items, check if they're in our date range
            if item.recurrence_pattern == 'none':
                if item.start_time.date() >= self.start_date and item.start_time.date() <= self.end_date:
                    expanded_items.append(item)
                continue
            
            # For recurring items, generate instances within our date range
            current_date = max(self.start_date, item.start_time.date())
            end_recurrence = item.recurrence_end_date or self.end_date
            
            while current_date <= min(self.end_date, end_recurrence):
                # Check if this instance should be included based on recurrence pattern
                include = False
                
                if item.recurrence_pattern == 'daily':
                    include = True
                elif item.recurrence_pattern == 'weekly' and current_date.weekday() == item.start_time.date().weekday():
                    include = True
                elif item.recurrence_pattern == 'monthly' and current_date.day == item.start_time.date().day:
                    include = True
                
                if include:
                    # Create a new datetime for this instance
                    start_time = datetime.datetime.combine(
                        current_date,
                        item.start_time.time()
                    )
                    end_time = datetime.datetime.combine(
                        current_date,
                        item.end_time.time()
                    )
                    
                    # If end time is earlier than start time, it spans to the next day
                    if end_time < start_time:
                        end_time += datetime.timedelta(days=1)
                    
                    # Create a virtual item for this instance
                    expanded_items.append({
                        'id': item.id,
                        'title': item.title,
                        'start_time': start_time,
                        'end_time': end_time,
                        'priority': item.priority
                    })
                
                # Move to next day
                if item.recurrence_pattern == 'daily':
                    current_date += datetime.timedelta(days=1)
                elif item.recurrence_pattern == 'weekly':
                    current_date += datetime.timedelta(days=7)
                elif item.recurrence_pattern == 'monthly':
                    # Move to the same day next month
                    if current_date.month == 12:
                        next_month = 1
                        next_year = current_date.year + 1
                    else:
                        next_month = current_date.month + 1
                        next_year = current_date.year
                    
                    # Handle month length differences
                    try:
                        current_date = current_date.replace(year=next_year, month=next_month)
                    except ValueError:
                        # Day doesn't exist in next month, use last day
                        if next_month == 2:
                            # February special case
                            if (next_year % 4 == 0 and next_year % 100 != 0) or next_year % 400 == 0:
                                current_date = current_date.replace(year=next_year, month=next_month, day=29)
                            else:
                                current_date = current_date.replace(year=next_year, month=next_month, day=28)
                        else:
                            # Use last day of month
                            last_day = 30 if next_month in [4, 6, 9, 11] else 31
                            current_date = current_date.replace(year=next_year, month=next_month, day=last_day)
        
        return expanded_items
    
    def get_free_time_blocks(self):
        """
        Identify all free time blocks between fixed schedule items.
        
        Returns:
            List of dictionaries with start_time and end_time for each free block
        """
        fixed_items = self.get_fixed_schedule_items()
        
        # Sort fixed items by start time
        fixed_items.sort(key=lambda x: x['start_time'] if isinstance(x, dict) else x.start_time)
        
        free_blocks = []
        current_date = self.start_date
        
        # Process each day in the date range
        while current_date <= self.end_date:
            # Start of day's available time
            day_start = datetime.datetime.combine(current_date, self.start_day_time)
            day_end = datetime.datetime.combine(current_date, self.end_day_time)
            
            # Get fixed items for this day
            day_items = [
                item for item in fixed_items 
                if (isinstance(item, dict) and item['start_time'].date() == current_date) or
                   (not isinstance(item, dict) and item.start_time.date() == current_date)
            ]
            
            if not day_items:
                # No fixed items today, entire day is free
                if (day_end - day_start).total_seconds() / 60 >= self.min_block_duration:
                    free_blocks.append({
                        'start_time': day_start,
                        'end_time': day_end,
                        'duration_minutes': (day_end - day_start).total_seconds() / 60
                    })
            else:
                # Check for free time before first item
                first_item_start = day_items[0]['start_time'] if isinstance(day_items[0], dict) else day_items[0].start_time
                if first_item_start > day_start and (first_item_start - day_start).total_seconds() / 60 >= self.min_block_duration:
                    free_blocks.append({
                        'start_time': day_start,
                        'end_time': first_item_start,
                        'duration_minutes': (first_item_start - day_start).total_seconds() / 60
                    })
                
                # Check for free time between items
                for i in range(len(day_items) - 1):
                    current_item_end = day_items[i]['end_time'] if isinstance(day_items[i], dict) else day_items[i].end_time
                    next_item_start = day_items[i+1]['start_time'] if isinstance(day_items[i+1], dict) else day_items[i+1].start_time
                    
                    if next_item_start > current_item_end and (next_item_start - current_item_end).total_seconds() / 60 >= self.min_block_duration:
                        free_blocks.append({
                            'start_time': current_item_end,
                            'end_time': next_item_start,
                            'duration_minutes': (next_item_start - current_item_end).total_seconds() / 60
                        })
                
                # Check for free time after last item
                last_item_end = day_items[-1]['end_time'] if isinstance(day_items[-1], dict) else day_items[-1].end_time
                if day_end > last_item_end and (day_end - last_item_end).total_seconds() / 60 >= self.min_block_duration:
                    free_blocks.append({
                        'start_time': last_item_end,
                        'end_time': day_end,
                        'duration_minutes': (day_end - last_item_end).total_seconds() / 60
                    })
            
            # Move to next day
            current_date += datetime.timedelta(days=1)
        
        return free_blocks
    
    def get_pending_tasks(self):
        """Get all pending tasks for the user."""
        return Task.query.filter_by(user_id=self.user_id, status='pending').all()
    
    def calculate_task_score(self, task, time_block, current_time):
        """
        Calculate a score for scheduling a task in a specific time block.
        Higher score means better fit.
        
        Args:
            task: Task object
            time_block: Dictionary with start_time and end_time
            current_time: Current datetime for deadline calculations
        
        Returns:
            Score value (higher is better)
        """
        # Base score
        score = 0
        
        # Factor 1: Does the task fit in the time block?
        if task.estimated_duration <= time_block['duration_minutes']:
            score += 100  # Base score for fitting
        else:
            return -1  # Task doesn't fit, return negative score
        
        # Factor 2: Priority bonus (0-40 points)
        score += (task.priority - 1) * 10  # 0-40 points based on priority (1-5)
        
        # Factor 3: Deadline proximity (0-30 points)
        if task.deadline:
            time_until_deadline = (task.deadline - current_time).total_seconds() / 3600  # hours
            if time_until_deadline <= 0:
                # Overdue tasks get maximum urgency
                score += 30
            elif time_until_deadline <= 24:
                # Due within 24 hours
                score += 25
            elif time_until_deadline <= 72:
                # Due within 3 days
                score += 20
            elif time_until_deadline <= 168:
                # Due within a week
                score += 15
            else:
                # Due later
                score += 5
        
        # Factor 4: Block utilization (0-20 points)
        # Prefer blocks that the task fills more completely
        utilization = task.estimated_duration / time_block['duration_minutes']
        score += utilization * 20
        
        # Factor 5: Time of day preference (0-10 points)
        # This would ideally come from user preferences or learning
        # For now, use a simple heuristic based on time of day
        hour = time_block['start_time'].hour
        if 9 <= hour <= 12:
            # Morning (9 AM - 12 PM): good for focused work
            score += 10
        elif 13 <= hour <= 16:
            # Afternoon (1 PM - 4 PM): good for collaborative work
            score += 8
        elif 17 <= hour <= 19:
            # Evening (5 PM - 7 PM): good for lighter tasks
            score += 6
        else:
            # Early morning or late evening: less preferred
            score += 3
        
        return score
    
    def generate_schedule(self):
        """
        Generate an optimal schedule for pending tasks.
        
        Returns:
            List of scheduled blocks
        """
        # Get free time blocks
        free_blocks = self.get_free_time_blocks()
        
        # Get pending tasks
        pending_tasks = self.get_pending_tasks()
        
        # Sort tasks by priority and deadline
        pending_tasks.sort(key=lambda t: (
            -t.priority,  # Higher priority first
            t.deadline or datetime.datetime.max  # Earlier deadline first
        ))
        
        # Current time for deadline calculations
        current_time = datetime.datetime.now()
        
        # Schedule tasks
        scheduled_blocks = []
        
        for task in pending_tasks:
            # Find best time block for this task
            best_block = None
            best_score = -1
            
            for block in free_blocks:
                score = self.calculate_task_score(task, block, current_time)
                if score > best_score:
                    best_score = score
                    best_block = block
            
            if best_block:
                # Schedule the task in this block
                scheduled_block = ScheduledBlock(
                    user_id=self.user_id,
                    task_id=task.id,
                    start_time=best_block['start_time'],
                    end_time=best_block['start_time'] + datetime.timedelta(minutes=task.estimated_duration),
                    status='suggested'
                )
                
                # Update the free block
                remaining_minutes = best_block['duration_minutes'] - task.estimated_duration
                if remaining_minutes >= self.min_block_duration:
                    # Block still has usable time, update it
                    best_block['start_time'] = scheduled_block.end_time
                    best_block['duration_minutes'] = remaining_minutes
                else:
                    # Block is now too small, remove it
                    free_blocks.remove(best_block)
                
                scheduled_blocks.append(scheduled_block)
                
                # Update task status
                task.status = 'scheduled'
        
        # Save to database
        for block in scheduled_blocks:
            db.session.add(block)
        
        db.session.commit()
        
        return scheduled_blocks

def schedule_tasks_for_user(user_id, start_date=None, end_date=None):
    """
    Schedule tasks for a specific user.
    
    Args:
        user_id: User ID
        start_date: Start date for scheduling (defaults to today)
        end_date: End date for scheduling (defaults to 7 days from start)
    
    Returns:
        List of scheduled blocks
    """
    scheduler = IntelligentScheduler(user_id, start_date, end_date)
    return scheduler.generate_schedule()
