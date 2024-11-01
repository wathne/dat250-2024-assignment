"""Provides all routes for the Social Insecurity application.

This file contains the routes for the application. It is imported by the social_insecurity package.
It also contains the SQL queries used for communicating with the database.
"""

from pathlib import Path

from flask import current_app as app
from flask import flash, redirect, render_template, send_from_directory, url_for
from flask import g # g is a LocalProxy.
from flask import session # session is a LocalProxy.
from flask.ctx import _AppCtxGlobals as ACG # g type.
from flask.sessions import SecureCookieSession as SCS # session type.

from social_insecurity import sqlite, bcrypt
from social_insecurity.forms import CommentsForm, FriendsForm, IndexForm, PostForm, ProfileForm
from social_insecurity.sessions_handler import load_user

from typing import cast

from werkzeug.exceptions import BadRequest # 400
from werkzeug.exceptions import Unauthorized # 401
from werkzeug.local import LocalProxy
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    """Provides the index page for the application.

    It reads the composite IndexForm and based on which form was submitted,
    it either logs the user in or registers a new user.

    If no form was submitted, it simply renders the index page.
    """
    index_form = IndexForm()
    login_form = index_form.login
    register_form = index_form.register

    if login_form.is_submitted() and login_form.submit.data:
        if not login_form.validate_on_submit():
            flash("Your submitted form data is not valid.", category="warning")
        else:
            # Retrieve login credentials from the login form data.
            username: str | None = None
            password: str | None = None
            if (isinstance(login_form.username.data, str)
                    and not login_form.username.data == ""):
                username = login_form.username.data
            if (isinstance(login_form.password.data, str)
                    and not login_form.password.data == ""):
                password = login_form.password.data
            if username is None:
                raise BadRequest(description="No username.")
            if password is None:
                raise BadRequest(description="No password.")

            # Set login credentials in the Secure Cookie Session (SCS).
            # pylint: disable=protected-access
            scs: SCS = cast(LocalProxy[SCS], session)._get_current_object()
            scs["username"] = username
            scs["password"] = password

            # load_user() will validate the cookie session against the SQLite3
            # database.
            load_user()

            # Retrieve user data from the Application Context Globals (ACG).
            # acg.user_id is an Application Context Global (ACG) variable. This
            # global variable will indicate if the user has a valid cookie
            # session.
            # acg.user_id is set to None if load_user() failed a check.
            # acg.user_id is set to an integer if load_user() passed all checks.
            # pylint: disable=protected-access
            acg: ACG = cast(LocalProxy[ACG], g)._get_current_object()
            if acg.user_id is None:
                print("Login failed.")
                flash(
                    "Your login credentials are not valid.",
                    category="warning",
                )
                #raise Unauthorized(description="Not logged in.")
            else:
                print(f"Login as user_id: {acg.user_id}.")
                flash((
                    f"You are logged in as {acg.user_username}"
                    f" with user id {acg.user_id}."
                    ),
                    category="info",
                )
                return redirect(url_for(
                    "stream",
                    username=login_form.username.data,
                ))
            #TODO(wathne): Should we use these original flash messages?
            # flash("Sorry, this user does not exist!", category="warning")
            # flash("Sorry, wrong password!", category="warning")

    elif register_form.is_submitted() and register_form.submit.data:
        if not register_form.validate_on_submit():
            flash("Your submitted form data is not valid.", category="warning")
        else:
            hashed_password = register_form.hash_password(bcrypt)
            insert_user = """
                INSERT INTO Users (username, first_name, last_name, password)
                VALUES (?, ?, ?, ?);
                """
            sqlite.query(insert_user, register_form.username.data, register_form.first_name.data, register_form.last_name.data, hashed_password )
            flash("User successfully created!", category="success")
            return redirect(url_for("index"))

    return render_template("index.html.j2", title="Welcome", form=index_form)


@app.route("/stream/<string:username>", methods=["GET", "POST"])
def stream(username: str):
    """Provides the stream page for the application.

    If a form was submitted, it reads the form data and inserts a new post into the database.

    Otherwise, it reads the username from the URL and displays all posts from the user and their friends.
    """
    post_form = PostForm()
    get_user = """
        SELECT *
        FROM Users
        WHERE username = ?;
        """
    user = sqlite.query(get_user, username, one=True)

    if post_form.validate_on_submit():
        secure_filename_: str = secure_filename(filename=post_form.image.data.filename)
        if post_form.image.data:
            path = Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"] / secure_filename_
            post_form.image.data.save(path)

        insert_post = """
            INSERT INTO Posts (u_id, content, image, creation_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP);
            """
        sqlite.query(insert_post,
                     user["id"],
                     post_form.content.data,
                     secure_filename_
                     )
        return redirect(url_for("stream", username=username))

    get_posts = """
         SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id = p.id) AS cc
         FROM Posts AS p JOIN Users AS u ON u.id = p.u_id
         WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id = ?) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id = ?) OR p.u_id = ?
         ORDER BY p.creation_time DESC;
        """
    posts = sqlite.query(get_posts,
                         user["id"],
                         user["id"],
                         user["id"]
                         )
    return render_template("stream.html.j2", title="Stream", username=username, form=post_form, posts=posts)


@app.route("/comments/<string:username>/<int:post_id>", methods=["GET", "POST"])
def comments(username: str, post_id: int):
    """Provides the comments page for the application.

    If a form was submitted, it reads the form data and inserts a new comment into the database.

    Otherwise, it reads the username and post id from the URL and displays all comments for the post.
    """
    comments_form = CommentsForm()
    get_user = """
        SELECT *
        FROM Users
        WHERE username = ?;
        """
    user = sqlite.query(get_user, username, one=True)

    if comments_form.validate_on_submit():
        insert_comment = """
            INSERT INTO Comments (p_id, u_id, comment, creation_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP);
            """
        sqlite.query(insert_comment,
                     post_id,
                     user["id"],
                     comments_form.comment.data
                     )

    get_post = """
        SELECT *
        FROM Posts AS p JOIN Users AS u ON p.u_id = u.id
        WHERE p.id = ?;
        """
    get_comments = """
        SELECT DISTINCT *
        FROM Comments AS c JOIN Users AS u ON c.u_id = u.id
        WHERE c.p_id= ?
        ORDER BY c.creation_time DESC;
        """
    post = sqlite.query(get_post, post_id, one=True)
    comments = sqlite.query(get_comments, post_id)
    return render_template(
        "comments.html.j2", title="Comments", username=username, form=comments_form, post=post, comments=comments
    )


@app.route("/friends/<string:username>", methods=["GET", "POST"])
def friends(username: str):
    """Provides the friends page for the application.

    If a form was submitted, it reads the form data and inserts a new friend into the database.

    Otherwise, it reads the username from the URL and displays all friends of the user.
    """

    load_user()
    # pylint: disable=protected-access
    acg: ACG = cast(LocalProxy[ACG], g)._get_current_object()
    if acg.user_id is None:
        raise Unauthorized(description="Not logged in.")
    if acg.user_username != username:
        raise Unauthorized(description=(f"Not logged in as {username}."))

    friends_form = FriendsForm()
    get_user = """
        SELECT *
        FROM Users
        WHERE username = ?;
        """
    user = sqlite.query(get_user, username, one=True)

    if friends_form.validate_on_submit():
        get_friend = """
            SELECT *
            FROM Users
            WHERE username = ?;
            """
        friend = sqlite.query(get_friend,friends_form.username.data, one=True)
        get_friends = """
            SELECT f_id
            FROM Friends
            WHERE u_id = ?;
            """
        friends = sqlite.query(get_friends,user["id"])

        if friend is None:
            flash("User does not exist!", category="warning")
        elif friend["id"] == user["id"]:
            flash("You cannot be friends with yourself!", category="warning")
        elif friend["id"] in [friend["f_id"] for friend in friends]:
            flash("You are already friends with this user!", category="warning")
        else:
            insert_friend = """
                INSERT INTO Friends (u_id, f_id)
                VALUES (?, ?);
                """
            sqlite.query(insert_friend, user["id"], friend["id"])
            flash("Friend successfully added!", category="success")

    get_friends = """
        SELECT *
        FROM Friends AS f JOIN Users as u ON f.f_id = u.id
        WHERE f.u_id = ? AND f.f_id != ?;
        """
    friends = sqlite.query(get_friends, user["id"], user["id"])
    return render_template("friends.html.j2", title="Friends", username=username, friends=friends, form=friends_form)


@app.route("/profile/<string:username>", methods=["GET", "POST"])
def profile(username: str):
    """Provides the profile page for the application.

    If a form was submitted, it reads the form data and updates the user's profile in the database.

    Otherwise, it reads the username from the URL and displays the user's profile.
    """

    load_user()
    # pylint: disable=protected-access
    acg: ACG = cast(LocalProxy[ACG], g)._get_current_object()
    if acg.user_id is None:
        raise Unauthorized(description="Not logged in.")
    if acg.user_username != username:
        raise Unauthorized(description=(f"Not logged in as {username}."))

    profile_form = ProfileForm()
    get_user = """
        SELECT *
        FROM Users
        WHERE username = ?;
        """
    user = sqlite.query(get_user, username, one=True)

    if profile_form.validate_on_submit():
        update_profile = """
            UPDATE Users
            SET education= ?, employment= ?,
                music= ?, movie= ?,
                nationality= ?, birthday= ?
            WHERE username= ?;
            """
        sqlite.query(update_profile,
                     profile_form.education.data,
                     profile_form.employment.data,
                     profile_form.music.data,
                     profile_form.movie.data,
                     profile_form.nationality.data,
                     profile_form.birthday.data,
                     username)
        return redirect(url_for("profile", username=username))

    return render_template("profile.html.j2", title="Profile", username=username, user=user, form=profile_form)


@app.route("/uploads/<string:filename>")
def uploads(filename):
    """Provides an endpoint for serving uploaded files."""
    return send_from_directory(Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"], filename)
