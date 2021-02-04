from flask_wtf import Form
from wtforms import StringField, SubmitField, validators, PasswordField
from wtforms.fields.html5 import EmailField
#from moniter_app.database import *

class FormLogin(Form):
    username = StringField('UserName', validators=[
        validators.DataRequired(),
        validators.Length(1, 15)
    ])
    password = PasswordField('PassWord', validators=[
        validators.DataRequired(),
        validators.Length(1, 15)
    ])
    submit = SubmitField('Login')