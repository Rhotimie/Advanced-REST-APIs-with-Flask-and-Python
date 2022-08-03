import os

"""
if APPLICATION_SETTINGS=default_config.py in .env file, we are using our test/local dvelopment config
This is used to set the properties that will be set in our app's config
This consist of the configuration that our application will ship with by default
This consist of default settings that are not passwords
"""
DEBUG = True
# SQLALCHEMY_DATABASE_URI = 'sqlite: // /data.db'
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Abraham1990@localhost/flask_db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
# This allows other extension like Flak_JWT to raise their own custom errors like 404 instead server errors(500)
PROPAGATE_EXCEPTIONS = True
# _IMAGES_ must be the same with "images" in IMAGE_SET = UploadSet("images", IMAGES) inside image_helper.py
UPLOADED_IMAGES_DEST = os.path.join("static", "images")  # manage root folder
"""
The below code is used to encrypt JWT secret key and this is an example of requiring a variable from the .env file
to be set before running the default_config file and that's why load_dotenv(".env", verbose=True) is above 
app.config.from_object("default_config") in app.py

os.environ.get("JWT_SECRET_KEY") will still parse if there is no "JWT_SECRET_KEY" set in .env file but it is better to
let the application crash if "JWT_SECRET_KEY" is not set, that is why we are using os.environ["JWT_SECRET_KEY"] instead
"""
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
# This is usually use for cookies
SECRET_KEY = os.environ["APP_SECRET_KEY"]
# enable blacklist feature
JWT_BLACKLIST_ENABLED = True
# allow blacklisting for access and refresh tokens
JWT_BLACKLIST_TOKEN_CHECKS = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
