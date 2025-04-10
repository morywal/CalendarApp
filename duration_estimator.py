import os
import sys
from app.models.models import Task, User
from app import db
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import pickle
import re

class TaskDurationEstimator:
    """
    A more sophisticated task duration estimator that uses machine learning
    to predict task durations based on task properties and user history.
    """
    
    def __init__(self, model_path=None):
        """Initialize the estimator, optionally loading a pre-trained model."""
        self.model = None
        self.vectorizer = None
        self.default_duration = 60  # Default duration in minutes
        
        # Try to load pre-trained model if path is provided
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.vectorizer = model_data['vectorizer']
                print(f"Loaded pre-trained model from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
    
    def extract_features(self, title, description, category):
        """Extract features from task properties."""
        # Combine text features
        text = f"{title} {description} {category}".lower()
        
        # Extract explicit duration mentions (e.g., "30 minutes", "2 hours")
        duration_mentions = self._extract_duration_mentions(text)
        
        # Count words as a proxy for complexity
        word_count = len(re.findall(r'\b\w+\b', text))
        
        # Extract category as a feature
        category_features = self._extract_category_features(category)
        
        return {
            'text': text,
            'duration_mentions': duration_mentions,
            'word_count': word_count,
            'category_features': category_features
        }
    
    def _extract_duration_mentions(self, text):
        """Extract explicit mentions of time durations from text."""
        # Look for patterns like "30 minutes", "2 hours", etc.
        minute_pattern = r'(\d+)\s*(?:min(?:ute)?s?)'
        hour_pattern = r'(\d+)\s*(?:hour|hr)s?'
        
        minutes = 0
        
        # Extract minutes
        minute_matches = re.findall(minute_pattern, text)
        if minute_matches:
            minutes += sum(int(m) for m in minute_matches)
        
        # Extract hours and convert to minutes
        hour_matches = re.findall(hour_pattern, text)
        if hour_matches:
            minutes += sum(int(h) * 60 for h in hour_matches)
        
        return minutes
    
    def _extract_category_features(self, category):
        """Extract features from the task category."""
        category = category.lower() if category else ""
        
        # Define category multipliers based on typical duration patterns
        category_multipliers = {
            'work': 1.2,
            'study': 1.1,
            'research': 1.3,
            'writing': 1.2,
            'reading': 0.9,
            'email': 0.7,
            'meeting': 1.0,
            'call': 0.8,
            'exercise': 0.8,
            'personal': 0.9,
            'shopping': 0.8,
            'cleaning': 0.9,
            'cooking': 0.8,
            'travel': 1.1,
            'project': 1.3,
            'assignment': 1.2,
            'exam': 1.2,
            'presentation': 1.1,
            'report': 1.2,
            'planning': 0.9,
            'design': 1.2,
            'development': 1.3,
            'testing': 1.0,
            'debugging': 1.2,
            'review': 0.9,
            'analysis': 1.1
        }
        
        # Find matching categories
        multiplier = 1.0
        for cat, mult in category_multipliers.items():
            if cat in category:
                multiplier = mult
                break
        
        return {
            'category_multiplier': multiplier
        }
    
    def predict_duration(self, title, description, category, user_id=None):
        """
        Predict task duration based on task properties and user history.
        
        If a trained model is available, use it for prediction.
        Otherwise, fall back to rule-based estimation.
        """
        # Extract features
        features = self.extract_features(title, description, category)
        
        # If explicit duration is mentioned, use that as a strong signal
        if features['duration_mentions'] > 0:
            return features['duration_mentions']
        
        # If we have a trained model, use it
        if self.model is not None and self.vectorizer is not None:
            try:
                # Transform text using vectorizer
                text_features = self.vectorizer.transform([features['text']])
                
                # Combine with other features
                X = np.hstack([
                    text_features.toarray(),
                    np.array([[
                        features['word_count'],
                        features['category_features']['category_multiplier']
                    ]])
                ])
                
                # Predict duration
                predicted_duration = self.model.predict(X)[0]
                
                # Round to nearest 5 minutes and ensure minimum duration
                return max(15, round(predicted_duration / 5) * 5)
            except Exception as e:
                print(f"Error using ML model: {e}")
                # Fall back to rule-based estimation
        
        # Rule-based estimation
        return self._rule_based_estimation(title, description, category, features)
    
    def _rule_based_estimation(self, title, description, category, features=None):
        """Rule-based estimation as a fallback."""
        if features is None:
            features = self.extract_features(title, description, category)
        
        # Start with default duration
        estimated_duration = self.default_duration
        
        # Adjust based on word count (proxy for complexity)
        if features['word_count'] < 5:
            estimated_duration *= 0.8  # Very short description
        elif features['word_count'] > 20:
            estimated_duration *= 1.2  # Longer description suggests complexity
        
        # Adjust based on category
        estimated_duration *= features['category_features']['category_multiplier']
        
        # Simple keyword-based adjustments
        text = features['text']
        keywords = {
            'quick': 0.5,
            'brief': 0.5,
            'short': 0.7,
            'small': 0.7,
            'simple': 0.7,
            'easy': 0.7,
            'basic': 0.8,
            'medium': 1.0,
            'average': 1.0,
            'standard': 1.0,
            'normal': 1.0,
            'complex': 1.3,
            'complicated': 1.3,
            'difficult': 1.3,
            'hard': 1.3,
            'challenging': 1.3,
            'long': 1.5,
            'big': 1.5,
            'large': 1.5,
            'extensive': 1.8,
            'comprehensive': 1.8,
            'thorough': 1.8,
            'detailed': 1.5,
            'in-depth': 1.7
        }
        
        # Check for keywords
        for keyword, multiplier in keywords.items():
            if keyword in text:
                estimated_duration *= multiplier
                break
        
        # Round to nearest 5 minutes
        estimated_duration = round(estimated_duration / 5) * 5
        
        # Ensure minimum duration of 15 minutes
        return max(15, estimated_duration)
    
    def train_model(self, tasks):
        """
        Train a machine learning model on historical task data.
        
        Args:
            tasks: List of Task objects with actual_duration values
        """
        if not tasks:
            print("No tasks available for training")
            return False
        
        # Filter tasks with actual duration
        tasks_with_duration = [t for t in tasks if t.actual_duration is not None]
        
        if len(tasks_with_duration) < 5:
            print(f"Not enough tasks with actual duration for training: {len(tasks_with_duration)}")
            return False
        
        # Prepare training data
        texts = []
        features = []
        durations = []
        
        for task in tasks_with_duration:
            # Extract text features
            text = f"{task.title} {task.description or ''} {task.category or ''}".lower()
            texts.append(text)
            
            # Extract other features
            task_features = self.extract_features(task.title, task.description or '', task.category or '')
            features.append([
                task_features['word_count'],
                task_features['category_features']['category_multiplier']
            ])
            
            # Target variable
            durations.append(task.actual_duration)
        
        # Create and fit vectorizer
        self.vectorizer = TfidfVectorizer(max_features=100)
        text_features = self.vectorizer.fit_transform(texts)
        
        # Combine features
        X = np.hstack([text_features.toarray(), np.array(features)])
        y = np.array(durations)
        
        # Train model
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        print(f"Trained model on {len(tasks_with_duration)} tasks")
        return True
    
    def save_model(self, model_path):
        """Save the trained model to disk."""
        if self.model is None or self.vectorizer is None:
            print("No trained model to save")
            return False
        
        try:
            model_dir = os.path.dirname(model_path)
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'vectorizer': self.vectorizer
                }, f)
            print(f"Model saved to {model_path}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def update_model_with_feedback(self, user_id):
        """Update the model with new user feedback."""
        # Get all tasks with actual duration for this user
        tasks = Task.query.filter_by(user_id=user_id).filter(Task.actual_duration.isnot(None)).all()
        
        if not tasks or len(tasks) < 5:
            print(f"Not enough tasks with feedback for user {user_id}")
            return False
        
        # Train model with these tasks
        success = self.train_model(tasks)
        
        if success:
            # Save model to user-specific path
            model_dir = os.path.join('app', 'models', 'trained', str(user_id))
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            
            model_path = os.path.join(model_dir, 'duration_model.pkl')
            self.save_model(model_path)
        
        return success

# Function to get user-specific estimator
def get_duration_estimator(user_id=None):
    """Get a duration estimator, optionally user-specific if trained model exists."""
    if user_id:
        # Check for user-specific model
        model_path = os.path.join('app', 'models', 'trained', str(user_id), 'duration_model.pkl')
        if os.path.exists(model_path):
            return TaskDurationEstimator(model_path=model_path)
    
    # Fall back to default estimator
    return TaskDurationEstimator()

# Function to suggest task duration
def suggest_task_duration(title, description, category, user_id=None):
    """Suggest a task duration based on task properties and user history."""
    estimator = get_duration_estimator(user_id)
    return estimator.predict_duration(title, description, category, user_id)
