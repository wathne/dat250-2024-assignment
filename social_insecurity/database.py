"""Provides a SQLite3 database extension for Flask.

This extension provides a simple interface to the SQLite3 database.

Example:
    from flask import Flask
    from social_insecurity.database import SQLite3

    app = Flask(__name__)
    db = SQLite3(app)
"""

from __future__ import annotations

from collections.abc import Callable
import sqlite3
from os import PathLike
from pathlib import Path
from typing import Any, Optional, cast

from flask import Flask, current_app, g


class SQLite3:
    """Provides a SQLite3 database extension for Flask.

    This class provides a simple interface to the SQLite3 database.
    It also initializes the database if it does not exist yet.

    Example:
        from flask import Flask
        from social_insecurity.database import SQLite3

        app = Flask(__name__)
        db = SQLite3(app)

        # Use the database
        # db.query("SELECT * FROM Users;")
        # db.query("SELECT * FROM Users WHERE id = 1;", one=True)
        # db.query("INSERT INTO Users (name, email) VALUES ('John', 'test@test.net');")
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        *,
        path: Optional[PathLike | str] = None,
        schema: Optional[PathLike | str] = None,
    ) -> None:
        """Initializes the extension.

        params:
            app: The Flask application to initialize the extension with.
            path (optional): The path to the database file. Is relative to the instance folder.
            schema (optional): The path to the schema file. Is relative to the application root folder.

        """
        if app is not None:
            self.init_app(app, path=path, schema=schema)

    def init_app(
        self,
        app: Flask,
        *,
        path: Optional[PathLike | str] = None,
        schema: Optional[PathLike | str] = None,
    ) -> None:
        """Initializes the extension.

        params:
            app: The Flask application to initialize the extension with.
            path (optional): The path to the database file. Is relative to the instance folder.
            schema (optional): The path to the schema file. Is relative to the application root folder.

        """
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "sqlite3" not in app.extensions:
            app.extensions["sqlite3"] = self
        else:
            raise RuntimeError("Flask SQLite3 extension already initialized")

        instance_path = Path(app.instance_path)
        database_path = path or app.config.get("SQLITE3_DATABASE_PATH")

        if database_path:
            if ":memory:" in str(database_path):
                self._path = Path(database_path)
            else:
                self._path = instance_path / database_path
        else:
            raise ValueError("No database path provided to SQLite3 extension")

        if not self._path.exists():
            self._path.parent.mkdir(parents=True)

        if schema and not self._path.exists():
            with app.app_context():
                self._init_database(schema)

        app.teardown_appcontext(self._close_connection)

    @property
    def connection(self) -> sqlite3.Connection:
        """Returns the connection to the SQLite3 database."""
        conn = getattr(g, "flask_sqlite3_connection", None)
        if conn is None:
            conn = g.flask_sqlite3_connection = sqlite3.connect(self._path)
            conn.row_factory = sqlite3.Row
        return conn

    def query(self, query: str, *args, one: bool = False) -> Any:
        """Queries the database and returns the result.'

        params:
            query: The SQL query to execute.
            one: Whether to return a single row or a list of rows.
            args: Additional arguments to pass to the query.

        returns: A single row, a list of rows or None.

        """
        cursor = self.connection.execute(query, args)
        response = cursor.fetchone() if one else cursor.fetchall()
        cursor.close()
        self.connection.commit()
        return response

    # TODO: Add more specific query methods to simplify code

    def retrieve_user_by_username(
        self,
        username: str,
    ) -> dict[str, str | int] | None:
        db_con: sqlite3.Connection = self.connection
        print("Database: Retrieving user ...")
        sql: str = (
            "SELECT "
                "id, "
                "username, "
                "password, "
                "first_name, "
                "last_name"
            " FROM Users WHERE username = :username;"
        )
        parameters: dict[str, str] = {
            "username": username,
        }
        db_cur: sqlite3.Cursor
        db_cur_row: sqlite3.Row
        rows: list[sqlite3.Row] = []
        row: sqlite3.Row
        user: dict[str, str | int] = {}
        try:
            with db_con:
                db_cur = db_con.cursor()
                db_cur.row_factory = cast(Callable[[sqlite3.Cursor,
                    sqlite3.Row], sqlite3.Row], sqlite3.Row)
                db_cur.execute(sql, parameters)
                # TODO(wathne): Limit this to one iteration.
                for db_cur_row in db_cur:
                    rows.append(db_cur_row)
        except sqlite3.Error as err:
            print(err)
            print("Database: User retrieval failed.")
            return None
        else:
            if not rows:
                print("Database: List of retrieved rows is empty.")
                print("Database: User retrieval failed.")
                return None
            row = rows[0]
            try:
                user["id"] = int(row["id"])
            except (TypeError, ValueError) as int_error:
                print(int_error)
                print("Database: User retrieval failed.")
                return None
            user["username"] = str(row["username"])
            user["password"] = str(row["password"])
            user["first_name"] = str(row["first_name"])
            user["last_name"] = str(row["last_name"])
            print("Database: User retrieval completed successfully.")
            return user
        finally:
            # The finally clause is always executed on the way out.
            db_cur.close()

    def _init_database(self, schema: PathLike | str) -> None:
        """Initializes the database with the supplied schema if it does not exist yet."""
        with current_app.open_resource(str(schema), mode="r") as file:
            self.connection.executescript(file.read())
            self.connection.commit()

    def _close_connection(self, exception: Optional[BaseException] = None) -> None:
        """Closes the connection to the database."""
        conn = cast(sqlite3.Connection, getattr(g, "flask_sqlite3_connection", None))
        if conn is not None:
            conn.close()
