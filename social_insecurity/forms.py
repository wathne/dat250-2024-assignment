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
                    Regexp('^[A-Za-z]*$')] 
    )
    password = PasswordField(
        label="Password", 
        render_kw={"placeholder": "Password"}, 
        validators=[DataRequired(), Length(min=5, max=20),
                    Regexp('^[A-Za-z0-9!@#$%^&*.]*$')]
    )
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField(label="Sign In")


class RegisterForm(FlaskForm):
    """Provides the registration form for the application."""

    first_name = StringField(
        label="First Name", 
        render_kw={"placeholder": "First Name"}, 
        validators=[DataRequired(message="First name is required."),
            Length(min=2, max=20, message="First name must be between 2 and 20 characters."),
            Regexp('^[A-Za-z]*$', message="First name can only contain letters.")]
    )
    
    last_name = StringField(
        label="Last Name", 
        render_kw={"placeholder": "Last Name"}, 
        validators=[DataRequired(message="Last name is required."),
            Length(min=2, max=20, message="Last name must be between 2 and 20 characters."),
            Regexp('^[A-Za-z]*$', message="Last name can only contain letters.")]
    )
    
    username = StringField(
        label="Username", 
        render_kw={"placeholder": "Username"}, 
        validators=[DataRequired(message="Username is required."),
            Length(min=3, max=15, message="Username must be between 3 and 15 characters."),
            Regexp('^[A-Za-z]*$', message="Username can only contain letters.")]
    )
    
    password = PasswordField(
        label="Password", 
        render_kw={"placeholder": "Password"}, 
        validators=[DataRequired(message="Password is required."),
            Length(min=5, max=20, message="Password must be between 5 and 20 characters."),
            Regexp('^[A-Za-z0-9!@#$%^&*.]*$', message="Password can only contain letters, numbers, and special characters !@#$%^&*.")]
    )
    
    confirm_password = PasswordField(
        label="Confirm Password", 
        render_kw={"placeholder": "Confirm Password"}, 
        validators=[DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")]
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
        validators=[
            DataRequired(message="Post content is required."),
            Length(max=1000, message="Post content cannot exceed 1000 characters."),
            Regexp('^[A-Za-z ]*$', message="Post content can only contain letters and spaces.")
        ]
    )
    image = FileField(label="Image")
    submit = SubmitField(label="Post")


class CommentsForm(FlaskForm):
    """Provides the comment form for the application."""

    comment = TextAreaField(
        label="New Comment", 
        render_kw={"placeholder": "What do you have to say?"}, 
        validators=[
            DataRequired(message="Comment content is required."),
            Length(max=1000, message="Comment content cannot exceed 1000 characters."),
            Regexp('^[A-Za-z ]*$', message="Comment content can only contain letters and spaces.")
        ]
    )
    submit = SubmitField(label="Comment")


class FriendsForm(FlaskForm):
    """Provides the friend form for the application."""

    username = StringField(
        label="Friend's username", 
        render_kw={"placeholder": "Username"}, 
        validators=[
            DataRequired(message="Friend's username is required."),
            Length(min=3, max=15, message="Username must be between 3 and 15 characters."),
            Regexp('^[A-Za-z]*$', message="Friend's username can only contain letters.")
        ]
    )
    submit = SubmitField(label="Add Friend")


class ProfileForm(FlaskForm):
    """Provides the profile form for the application."""

    education = StringField(
        label="Education", 
        render_kw={"placeholder": "Highest education"}, 
        validators=[
            Length(max=100, message="Education field cannot exceed 100 characters."),
            Regexp('^[A-Za-z ]*$', message="Education field can only contain letters and spaces.")
        ]
    )
    
    employment = StringField(
        label="Employment", 
        render_kw={"placeholder": "Current employment"}, 
        validators=[
            Length(max=100, message="Employment field cannot exceed 100 characters."),
            Regexp('^[A-Za-z ]*$', message="Employment field can only contain letters and spaces.")
        ]
    )
    
    music = StringField(
        label="Favorite song", 
        render_kw={"placeholder": "Favorite song"}, 
        validators=[
            Length(max=100, message="Favorite song cannot exceed 100 characters."),
            Regexp('^[A-Za-z ]*$', message="Favorite song can only contain letters and spaces.")
        ]
    )
    
    movie = StringField(
        label="Favorite movie", 
        render_kw={"placeholder": "Favorite movie"}, 
        validators=[
            Length(max=100, message="Favorite movie cannot exceed 100 characters."),
            Regexp('^[A-Za-z ]*$', message="Favorite movie can only contain letters and spaces.")
        ]
    )
    
    nationality = StringField(
        label="Nationality", 
        render_kw={"placeholder": "Your nationality"}, 
        validators=[
            Length(max=100, message="Nationality cannot exceed 100 characters."),
            Regexp('^[A-Za-z ]*$', message="Nationality can only contain letters and spaces.")
        ]
    )
    
    birthday = DateField(
        label="Birthday", 
        default=datetime.now(), 
        validators=[]
    )
    
    submit = SubmitField(label="Update Profile")
