import os

"""
if APPLICATION_SETTINGS=config.py in .env file, we are using our production config
This finds application when we deploy our application to the server
It overrides settings from the default config in default_config.py and use them as final configuration when our 
    application is shared with the user--anything not set here stays as the default!
It might use the environment variables. so load the .env files before using this config file
It is here we can switch our database from SQLite to PostGRE or MySQL
"""

DEBUG = False
# this use the value in "DATABASE_URL" if it is set otherwise use "postgresql://postgres:Abraham1990@localhost/flask_db"
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:Abraham1990@localhost/flask_db"
)
