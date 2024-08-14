from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, SubmitField, PasswordField, BooleanField, RadioField, SelectField, URLField, FileField

from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms.validators import DataRequired, Length




class DrycleanerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    genders=  RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    website=  URLField('Website', validators=[DataRequired()])
    idcard=  FileField('Idcard', validators=[DataRequired()])
    submit = SubmitField('Submit')



class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')


# class ContactForm(FlaskForm):
#     username = StringField('username', validators=[DataRequired(),Length(3)])
#     password = PasswordField('password', validators=[DataRequired()])
#     submit = SubmitField('Submit')

# class SignupForm(FlaskForm):
#     name=StringField('name', validators=[DataRequired()])
#     is_admin=BooleanField('is an Admin', validators=[DataRequired()])
#     submit = SubmitField('Submit')



class DpForm(FlaskForm):
    dp=FileField("Your Dp:",validators=[FileRequired(), FileAllowed(["jpg","png"],"invalid file format")])
    btnupload=SubmitField("Upload!")
