import base64
import uuid

from app import db, lm, team_icons

from flask import url_for
from passlib.apps import custom_app_context as pw_context
from sqlalchemy.dialects.postgresql import UUID

__all__ = ['User', 'Team']

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model):
    __tablename__ = 'users'

    # Important for logging in
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    pw_hash = db.Column(db.String, nullable=False)

    # Information we're collecting
    shirt_size = db.Column(
        db.Enum('S', 'M', 'L', 'XL', 'XXL',
                native_enum=False,
                name='shirt_size_name'),
        nullable=False,
        default='M'
    )

    # FOOD!
    food_preferences = db.Column(
        db.Enum('None', 'Vegetarian', 'Vegan', 'Gluten Free', 'Other',
                native_enum=False,
                name='food_preferences_types'),
        nullable=False,
        default='None'
    )
    food_other = db.Column(db.String, nullable=True)

    # Internal info
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    confirmation = db.Column(
        UUID(as_uuid=True),
        nullable=True,
        unique=True,
        default=uuid.uuid4)

    # This is really a thin wrapper around pw_hash so we can just set
    # password and have it update pw_hash
    @property
    def password(self):
        return self.pw_hash

    @password.setter
    def password(self, password):
        self.pw_hash = pw_context.encrypt(password)

    # This checks the pw in the model against the given password
    def check_password(self, password):
        return pw_context.verify(password, self.pw_hash)

    def is_authenticated(self):
        return True

    def is_active(self):
        # If the confirmation is None, we've confirmed our email
        return self.confirmation is None

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    secret = db.Column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        default=uuid.uuid4)
    members = db.relationship('User', backref='team')
    icon_name = db.Column(db.String, nullable=True)
    location = db.Column(
        db.Enum('MTU', 'NMU', 'WMU', 'Sponsor',
                native_enum=False,
                name='team_location'),
        nullable=False,
        default='MTU'
    )

    @property
    def icon_url(self):
        if self.icon_name is not None:
            return team_icons.url(self.icon_name)

        return url_for('static', filename='img/default_avatar.png')

    @property
    def is_remote(self):
        return self.location == 'WMU'

    # We list them as paid if they're a remote team because they don't need to
    # pay
    @property
    def is_paid(self):
        if self.location == 'Sponsor':
            return True

        return self.paid

    @property
    def is_full(self):
        return len(self.members) >= 3

    def __repr__(self):
        return '<Team %r>' % (self.name)
