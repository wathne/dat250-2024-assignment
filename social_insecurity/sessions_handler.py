"""Sessions handler.
"""

from flask import g # g is a LocalProxy.
from flask import session # session is a LocalProxy.
from flask.ctx import _AppCtxGlobals as ACG # g type.
from flask.sessions import SecureCookieSession as SCS # session type.
from social_insecurity import brycpt # bcrypt object initialized in __init__.py.
from social_insecurity import sqlite # sqlite object initialized in __init__.py.
from typing import cast
from werkzeug.local import LocalProxy

# load_user() will validate a cookie session against the SQLite3 database.
# acg.user_id is an Application Context Global (ACG) variable. This global
# variable will indicate if the user has a valid cookie session.
# acg.user_id is set to None if load_user() failed a check.
# acg.user_id is set to an integer if load_user() passed all checks.
def load_user() -> None:
    print("Calling load_user().")
    # pylint: disable=protected-access

    # Initialize the Application Context Globals (ACG) user data variables.
    acg: ACG = cast(LocalProxy[ACG], g)._get_current_object()
    acg.user_id = None
    acg.user_username = None
    acg.user_first_name = None
    acg.user_last_name = None

    # Retrieve login credentials from the Secure Cookie Session (SCS).
    scs: SCS = cast(LocalProxy[SCS], session)._get_current_object()
    scs_username: str | None = scs.get(key="username", default=None)
    scs_password: str | None = scs.get(key="password", default=None)
    if scs_username is None:
        return None
    if scs_password is None:
        return None

    # Retrieve user data from the SQLite3 database.
    user: dict[str, str | int] | None
    user_id: int | None
    user_username: str | None
    user_password_hash: str | None
    user_first_name: str | None
    user_last_name: str | None
    user = sqlite.retrieve_user_by_username(username=scs_username)
    if user is None:
        return None
    user_id = cast(int | None, user.get("id", None))
    user_username = cast(str | None, user.get("username", None))
    user_password_hash = cast(str | None, user.get("password", None))
    user_first_name = cast(str | None, user.get("first_name", None))
    user_last_name = cast(str | None, user.get("last_name", None))
    if user_id is None:
        return None
    if user_username is None:
        return None
    if user_password_hash is None:
        return None
    if user_first_name is None:
        return None
    if user_last_name is None:
        return None

    # Check the password.
    if bcrypt.check_password_hash(
        pw_hash=user_password_hash,
        password=scs_password,
    ):
        # Set the Application Context Globals (ACG) user data variables.
        acg.user_id = user_id
        acg.user_username = user_username
        acg.user_first_name = user_first_name
        acg.user_last_name = user_last_name
    return None
