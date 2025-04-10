from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, IntegerField, DateField, ColorField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class FixedScheduleItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    start_time = DateTimeField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    recurrence_pattern = SelectField('Recurrence', choices=[
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], default='none')
    recurrence_end_date = DateField('Recurrence End Date', format='%Y-%m-%d', validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High')
    ], default='3', coerce=int)
    category = StringField('Category', validators=[Optional(), Length(max=50)])
    color = ColorField('Color', default='#3788d8')
