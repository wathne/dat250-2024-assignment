"""Provides all forms used in the Social Insecurity application.

This file is used to define all forms used in the application.
It is imported by the social_insecurity package.
"""

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FileField,
    FormField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

# Defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields


class LoginForm(FlaskForm):
    """Provides the login form for the application."""
    
    username = StringField(
        label="Username", 
        render_kw={"placeholder": "Username"}, 
        validators=[DataRequired(), Length(min=3, max=15), 
                    Regexp('^A-Za-z0-9!@#$%^&*.*$')] 
    )
    password = PasswordField(
        label="Password", 
        render_kw={"placeholder": "Password"}, 
        validators=[DataRequired(), Length(min=5),
                    Regexp('^A-Za-z0-9!@#$%^&*.*$')]
    )
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField(label="Sign In")


class RegisterForm(FlaskForm):
    """Provides the registration form for the application."""

    first_name = StringField(
        label="First Name", 
        render_kw={"placeholder": "First Name"}, 
        validators=[DataRequired(), Length(min=2, max=20), 
                    Regexp('^[A-Za-z]*$')]
    )
    last_name = StringField(
        label="Last Name", 
        render_kw={"placeholder": "Last Name"}, 
        validators=[DataRequired(), Length(min=2, max=20), 
                    Regexp('^[A-Za-z]*$')]
    )
    username = StringField(
        label="Username", 
        render_kw={"placeholder": "Username"}, 
        validators=[DataRequired(), Length(min=3, max=15), 
                    Regexp('^[A-Za-z]*$')]
    )
    password = PasswordField(
        label="Password", 
        render_kw={"placeholder": "Password"}, 
        validators=[DataRequired(), Length(min=5), 
                    Regexp('^A-Za-z0-9!@#$%^&*.*$')]
    )
    confirm_password = PasswordField(
        label="Confirm Password", 
        render_kw={"placeholder": "Confirm Password"}, 
        validators=[DataRequired(), EqualTo('password', message="Passwords must match.")]
    )
    
    submit = SubmitField(label="Sign Up")

    def hash_password(self, bcrypt):
        """Hashes the password using bcrypt."""
        return bcrypt.generate_password_hash(self.password.data).decode('utf-8')

class IndexForm(FlaskForm):
    """Provides the composite form for the index page."""

    login = FormField(LoginForm)
    register = FormField(RegisterForm)


class PostForm(FlaskForm):
    """Provides the post form for the application."""

    content = TextAreaField(
        label="New Post", 
        render_kw={"placeholder": "What are you thinking about?"}, 
        validators=[DataRequired(), Length(max=1000), Regexp('^[A-Za-z]*$')]  
    )
    image = FileField(label="Image")
    submit = SubmitField(label="Post")


class CommentsForm(FlaskForm):
    """Provides the comment form for the application."""

    comment = TextAreaField(
        label="New Comment", 
        render_kw={"placeholder": "What do you have to say?"}, 
        validators=[DataRequired(), Length(max=1000), Regexp('^[A-Za-z]*$')]  
    )
    submit = SubmitField(label="Comment")


class FriendsForm(FlaskForm):
    """Provides the friend form for the application."""

    username = StringField(
        label="Friend's username", 
        render_kw={"placeholder": "Username"}, 
        validators=[DataRequired(), Length(min=3, max=20), Regexp('^[A-Za-z]*$')]
    )
    submit = SubmitField(label="Add Friend")


class ProfileForm(FlaskForm):
    """Provides the profile form for the application."""

    education = StringField(
        label="Education", 
        render_kw={"placeholder": "Highest education"}, 
        validators=[Length(max=100)] 
    )
    employment = StringField(
        label="Employment", 
        render_kw={"placeholder": "Current employment"}, 
        validators=[Length(max=100)] 
    )
    music = StringField(
        label="Favorite song", 
        render_kw={"placeholder": "Favorite song"}, 
        validators=[Length(max=100)] 
    )
    movie = StringField(
        label="Favorite movie", 
        render_kw={"placeholder": "Favorite movie"}, 
        validators=[Length(max=100)]
    )
    nationality = StringField(
        label="Nationality", 
        render_kw={"placeholder": "Your nationality"}, 
        validators=[Length(max=100)] 
    )
    birthday = DateField(label="Birthday", default=datetime.now())
    submit = SubmitField(label="Update Profile")
