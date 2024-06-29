# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, BooleanField, SubmitField, DateField, TelField, SelectField
from wtforms.validators import DataRequired, NumberRange, InputRequired


class ReservationForm(FlaskForm):
    num_people = SelectField('Cantidad de personas', choices=[(str(i), str(i)) for i in range(2, 9)], default='2',
                             validators=[InputRequired()])
    date = DateField('Fecha', validators=[DataRequired()], format='%Y-%m-%d')
    location = BooleanField('Indoor')
    timeslot = RadioField('Time Slot', choices=[], validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    phone = TelField('Teléfono', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reserve')
