from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ReservationForm(FlaskForm):
    num_people = IntegerField('Number of People', validators=[DataRequired(), NumberRange(min=1, max=20)])
    date = StringField('Date', validators=[DataRequired()])
    location = BooleanField('Indoor')
    timeslot = RadioField('Time Slot', choices=[], validators=[DataRequired()])
    submit = SubmitField('Reserve')
