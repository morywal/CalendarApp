# Calendar App Architecture

## System Architecture

The AI-powered calendar app will follow a client-server architecture with the following components:

1. **Frontend Layer**
   - Web-based user interface built with HTML, CSS, and JavaScript
   - Responsive design using Bootstrap
   - Interactive calendar using FullCalendar.js
   - Form components for schedule and task input
   - AJAX for asynchronous communication with backend

2. **Backend Layer**
   - Flask web application framework
   - RESTful API endpoints for data exchange
   - Authentication and authorization services
   - Business logic for scheduling algorithms
   - Task duration estimation module

3. **Data Layer**
   - SQLite database (development)
   - PostgreSQL database (production)
   - SQLAlchemy ORM for database interactions
   - Data models for users, schedules, tasks, and preferences

4. **AI/ML Layer**
   - Task duration estimation algorithm
   - Intelligent scheduling algorithm
   - User pattern recognition (future enhancement)

## Data Models

### User
- id: Integer (Primary Key)
- username: String
- email: String
- password_hash: String
- preferences: Relationship to UserPreferences

### UserPreferences
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- start_day_time: Time (e.g., 8:00 AM)
- end_day_time: Time (e.g., 10:00 PM)
- min_break_duration: Integer (minutes)
- preferred_task_duration: Integer (minutes)
- productivity_factors: JSON (time of day preferences)

### FixedScheduleItem
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String
- description: String (optional)
- start_time: DateTime
- end_time: DateTime
- recurrence_pattern: String (none, daily, weekly, monthly)
- recurrence_end_date: Date (optional)
- priority: Integer (1-5)
- category: String
- color: String (for UI display)

### Task
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String
- description: String
- deadline: DateTime
- estimated_duration: Integer (minutes)
- actual_duration: Integer (minutes, optional)
- priority: Integer (1-5)
- status: String (pending, scheduled, in_progress, completed)
- category: String
- dependencies: Relationship to TaskDependency

### TaskDependency
- id: Integer (Primary Key)
- task_id: Integer (Foreign Key)
- dependent_task_id: Integer (Foreign Key)

### ScheduledBlock
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- task_id: Integer (Foreign Key)
- start_time: DateTime
- end_time: DateTime
- status: String (suggested, confirmed, completed)

## Database Schema

```
+-------------------+       +----------------------+
| User              |       | UserPreferences      |
+-------------------+       +----------------------+
| id                |------>| id                   |
| username          |       | user_id              |
| email             |       | start_day_time       |
| password_hash     |       | end_day_time         |
+-------------------+       | min_break_duration   |
                            | preferred_task_duration |
                            | productivity_factors  |
                            +----------------------+
                                    ^
                                    |
+-------------------+       +----------------------+       +-------------------+
| FixedScheduleItem |       | Task                 |       | ScheduledBlock    |
+-------------------+       +----------------------+       +-------------------+
| id                |       | id                   |       | id                |
| user_id           |       | user_id              |       | user_id           |
| title             |       | title                |       | task_id           |
| description       |       | description          |       | start_time        |
| start_time        |       | deadline             |       | end_time          |
| end_time          |       | estimated_duration   |       | status            |
| recurrence_pattern|       | actual_duration      |       +-------------------+
| recurrence_end_date|      | priority             |
| priority          |       | status               |
| category          |       | category             |
| color             |       +----------------------+
+-------------------+               |
                                    |
                            +----------------------+
                            | TaskDependency       |
                            +----------------------+
                            | id                   |
                            | task_id              |
                            | dependent_task_id    |
                            +----------------------+
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user info

### Fixed Schedule
- `GET /api/schedule` - Get all fixed schedule items
- `POST /api/schedule` - Create new fixed schedule item
- `GET /api/schedule/{id}` - Get specific schedule item
- `PUT /api/schedule/{id}` - Update schedule item
- `DELETE /api/schedule/{id}` - Delete schedule item

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PUT /api/tasks/{id}/status` - Update task status
- `POST /api/tasks/{id}/dependencies` - Add task dependency

### Scheduling
- `GET /api/schedule/blocks` - Get all scheduled blocks
- `POST /api/schedule/generate` - Generate schedule suggestions
- `PUT /api/schedule/blocks/{id}` - Update scheduled block
- `DELETE /api/schedule/blocks/{id}` - Delete scheduled block

### User Preferences
- `GET /api/preferences` - Get user preferences
- `PUT /api/preferences` - Update user preferences

## Intelligent Scheduling Algorithm

The core of the application will be the intelligent scheduling algorithm that:

1. Identifies all available time blocks between fixed schedule items
2. Filters blocks based on user preferences (e.g., no work after 8 PM)
3. Sorts tasks by priority and deadline proximity
4. Matches tasks to appropriate time blocks based on:
   - Task duration vs. available block duration
   - Task priority
   - Deadline proximity
   - User productivity patterns
5. Handles task dependencies by scheduling dependent tasks after prerequisites
6. Provides buffer time between tasks when possible
7. Adapts to schedule changes and new task additions

## Task Duration Estimation

The task duration estimation module will:

1. Accept user input for estimated duration
2. Optionally suggest duration based on:
   - Task category
   - Task description keywords
   - Historical data from similar tasks
3. Apply adjustment factors based on:
   - User's historical accuracy in estimating
   - Task complexity indicators
   - Time of day (accounting for productivity variations)
4. Learn from actual completion times to improve future estimates
