from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, TextField, PasswordField, SelectField, TextAreaField
from wtforms.validators import Required, EqualTo, Email, Regexp

from app import db, app, team_icons
from app.models import *

__all__ = ['LoginForm', 'RegistrationForm', 'TeamForm', 'EditTeamForm', 'EditProfileForm', 'team_icons']

def tuple_to_choices(tup):
    choices = []
    for k in tup:
        choices.append((k, k))
    return choices

class LoginForm(Form):
    email = TextField('Email', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('User does not exist with that email')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True

class RegistrationForm(Form):
    name = TextField('Full Name', validators=[Required(),
                                              Regexp(
                                                  '^[A-Za-z]+ [A-Za-z ]*[A-Za-z]+$',
                                                  message='You must include both first and last name. Only letters are allowed.',
                                              )])
    email = TextField('Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    confirm = PasswordField('Confirm Password',
                            validators=[EqualTo('password',
                                                message='Passwords must match')])
    shirt_size = SelectField('Shirt Size', choices=tuple_to_choices(User.shirt_size.type.enums))
    food_preferences = SelectField('Food Preferences', choices=tuple_to_choices(User.food_preferences.type.enums))
    food_other = TextAreaField('Other Food Info')

    # We override the default because we need to look at multiple fields for one
    # value. We use this to validate the food portion.
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self._fields['food_preferences'].data != 'Other':
            self._fields['food_other'].data = None

        return True

    def save(self):
        user_data = {k: self.data[k] for k in ['name',
                                               'email',
                                               'password',
                                               'shirt_size',
                                               'food_preferences',
                                               'food_other']}
        user = User(**user_data)
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except:
            db.session.rollback()
            return None

class TeamForm(Form):
    name = TextField('Team Name', validators=[Required(),
                                              Regexp(
                                                  '^[A-Za-z0-9]?[A-Za-z0-9 ]*[A-Za-z0-9]$',
                                                  message='Only alpha-numeric characters are allowed.',
                                              )])
    location = SelectField('Location', choices=tuple_to_choices(Team.location.type.enums))
    icon = FileField('Team Icon',
                     validators=[FileRequired(),
                                 FileAllowed(team_icons, 'Images only!')])

class EditUserForm(RegistrationForm):
    shirt_size = SelectField('Shirt Size', choices=tuple_to_choices(User.shirt_size.type.enums))
    food_preferences = SelectField('Food Preferences', choices=tuple_to_choices(User.food_preferences.type.enums))
    food_other = TextAreaField('Other Food Info')

class EditProfileForm(Form):
  name = TextField('Full Name', validators=[Required(),
                                            Regexp(
                                                '^[A-Za-z]+ [A-Za-z ]*[A-Za-z]+$',
                                                message='You must include both first and last name. Only letters are allowed.',
                                            )])
  food_preferences = SelectField('Food Preferences', choices=tuple_to_choices(User.food_preferences.type.enums))
  food_other = TextAreaField('Other Food Info')

class EditTeamForm(TeamForm):
    icon = FileField('Team Icon',
                     validators=[FileAllowed(team_icons, 'Images only!')])
