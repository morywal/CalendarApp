import unittest
from app import create_app, db
from app.models.models import User, FixedScheduleItem, Task, ScheduledBlock
from app.models.duration_estimator import TaskDurationEstimator
from app.models.scheduler import IntelligentScheduler
from datetime import datetime, timedelta
import os
import tempfile

class CalendarAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            self.user_id = user.id
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login(self):
        """Helper function to log in"""
        return self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
    
    def test_home_page(self):
        """Test that home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI-Powered Calendar Assistant', response.data)
    
    def test_login(self):
        """Test user login functionality"""
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)
    
    def test_schedule_input(self):
        """Test schedule input functionality"""
        self.login()
        
        # Add a fixed schedule item
        response = self.client.post('/schedule/new', data={
            'title': 'Work',
            'description': 'Regular work hours',
            'start_time': '2025-04-07T09:00',
            'end_time': '2025-04-07T17:00',
            'recurrence_pattern': 'daily',
            'priority': '3',
            'category': 'Work',
            'color': '#3788d8'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Schedule item added successfully', response.data)
        
        # Check that the item was added to the database
        with self.app.app_context():
            items = FixedScheduleItem.query.filter_by(user_id=self.user_id).all()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].title, 'Work')
    
    def test_task_input(self):
        """Test task input functionality"""
        self.login()
        
        # Add a task
        response = self.client.post('/tasks/new', data={
            'title': 'Complete Project',
            'description': 'Finish the quarterly project report',
            'deadline': '2025-04-10T17:00',
            'estimated_duration': '120',
            'priority': '4',
            'category': 'Work'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task added successfully', response.data)
        
        # Check that the task was added to the database
        with self.app.app_context():
            tasks = Task.query.filter_by(user_id=self.user_id).all()
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].title, 'Complete Project')
            self.assertEqual(tasks[0].estimated_duration, 120)
    
    def test_duration_estimation(self):
        """Test task duration estimation algorithm"""
        with self.app.app_context():
            # Test the estimator directly
            estimator = TaskDurationEstimator()
            
            # Test with different task types
            quick_duration = estimator.predict_duration("Quick email reply", "Send a brief response", "Email")
            medium_duration = estimator.predict_duration("Weekly report", "Prepare the weekly status report", "Work")
            long_duration = estimator.predict_duration("Research project", "Comprehensive research on AI algorithms", "Study")
            
            # Verify that estimates make sense
            self.assertLess(quick_duration, medium_duration)
            self.assertLess(medium_duration, long_duration)
            
            # Test with explicit duration mentions
            explicit_duration = estimator.predict_duration("30 minute meeting", "Team standup", "Meeting")
            self.assertEqual(explicit_duration, 30)
    
    def test_intelligent_scheduling(self):
        """Test intelligent scheduling algorithm"""
        with self.app.app_context():
            # Create a user with fixed schedule and tasks
            user = User.query.get(self.user_id)
            
            # Add fixed schedule items
            work = FixedScheduleItem(
                user_id=self.user_id,
                title='Work',
                start_time=datetime.now().replace(hour=9, minute=0),
                end_time=datetime.now().replace(hour=17, minute=0),
                recurrence_pattern='daily',
                priority=3,
                category='Work'
            )
            
            lunch = FixedScheduleItem(
                user_id=self.user_id,
                title='Lunch',
                start_time=datetime.now().replace(hour=12, minute=0),
                end_time=datetime.now().replace(hour=13, minute=0),
                recurrence_pattern='daily',
                priority=2,
                category='Personal'
            )
            
            db.session.add_all([work, lunch])
            
            # Add tasks
            task1 = Task(
                user_id=self.user_id,
                title='Important Report',
                description='Complete quarterly report',
                deadline=datetime.now() + timedelta(days=2),
                estimated_duration=120,
                priority=5,
                category='Work',
                status='pending'
            )
            
            task2 = Task(
                user_id=self.user_id,
                title='Email Responses',
                description='Reply to emails',
                deadline=datetime.now() + timedelta(days=1),
                estimated_duration=30,
                priority=3,
                category='Work',
                status='pending'
            )
            
            db.session.add_all([task1, task2])
            db.session.commit()
            
            # Run the scheduler
            scheduler = IntelligentScheduler(self.user_id)
            blocks = scheduler.generate_schedule()
            
            # Verify that blocks were created
            self.assertGreater(len(blocks), 0)
            
            # Verify that high priority task is scheduled first
            high_priority_blocks = [b for b in blocks if b.task_id == task1.id]
            self.assertGreater(len(high_priority_blocks), 0)
            
            # Verify that blocks don't overlap with fixed schedule
            for block in blocks:
                # Check against work hours
                work_start = datetime.now().replace(hour=9, minute=0)
                work_end = datetime.now().replace(hour=17, minute=0)
                lunch_start = datetime.now().replace(hour=12, minute=0)
                lunch_end = datetime.now().replace(hour=13, minute=0)
                
                # Simplify check by just verifying block is not during lunch
                # (a more comprehensive test would check all fixed schedule items)
                if block.start_time.hour == lunch_start.hour:
                    self.assertFalse(lunch_start.hour <= block.start_time.hour < lunch_end.hour)

if __name__ == '__main__':
    unittest.main()
