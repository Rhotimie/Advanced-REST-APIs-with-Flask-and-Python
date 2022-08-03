import os
from flask import Flask, jsonify
from flask_restful import Api

# from flask_jwt import JWT
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from blacklist import BLACKLIST
from dotenv import load_dotenv
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate

from ma import ma
from db import db

"""
.env
storing any secrets of our app, because secrets keys can be stored on the server without putting them in the code
Things that may may change when we deploy can be included here like APPLICATION SETTINGS as this provides easy way
    of swaping between configs
Easy to use in code without keeping the values in our code
Easy to set in CI/CD pipelines directly onto the server
It is loaded automatically when we start our app but can be loaded before starting our app by using load_dotenv()
.env.example
This tell our users what environment variable they need
"""
# this is loaded here because our GithubLogin needs it
load_dotenv(".env", verbose=True)
# Note that this is asking for our environment variable even before loading them
from oa import oauth
from resources.user import (
    UserRegister,
    UserLogin,
    User,
    TokenRefresh,
    UserLogout,
    # UserConfirm,
    SetPassword,
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar
from resources.github_login import GithubLogin, GithubAuthorize
from resources.order import Order

# IMAGE_SET will be needed to configure uploads
from libs.image_helper import IMAGE_SET

app = Flask(__name__)
# this looks for object first inside the python file, if none, it then loads the constants inside the python file
# as config properties
app.config.from_object("default_config")  # load default configs from default_config.py
"""
this loads config from environment variables
override with default_config.py if APPLICATION_SETTINGS points to config.py with only the variables set in config.py, 
it doesn't change the variables not set in config.py that are in default_config.py
"""
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(
    app, 10 * 1024 * 1024
)  # restrict max upload image size to 10MB(10 bytes * kilo *mega)
configure_uploads(
    app, IMAGE_SET
)  # it activates uploads for the image set we have created

api = Api(app)

"""
JWT related configuration. The following functions includes:
1) add claims to each jwt
2) customize the token expired error message 
"""

jwt = JWTManager(app)

# This works together with SQLAlchemy very well
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


# setting app level error handlers
@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):  # except ValidationError as err
    return jsonify(err.messages), 400


"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below
"""


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    # instead of hard-coding, we should read from a config file to get a list of admins instead
    if identity == 2:
        return {"is_admin": True, "paid_user": True}
    return {"is_admin": False, "paid_user": False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # return decrypted_token['identity'] in BLACKLIST     # returns True if user_id is in blacklist or False if otherwise
    return decrypted_token["jti"] in BLACKLIST


# The following callbacks are configurations used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)

# this is called when flask_jwt realizes that the token sent to a client has expired when a client is
# trying to call jwt protected endpoint
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


# This is returned when the token sent from POSTMAN(example) in the Authorization header is not actual JWT
@jwt.invalid_token_loader
def invalid_token_callback(
    error,
):  # we have to keep the argument here, since it's passed in by the caller internally
    return (
        jsonify(
            {"message": "Signature(JWT) verification failed.", "error": "invalid_token"}
        ),
        401,
    )


# This is returned when a JWT is not sent at all from POSTMAN(example) in the Authorization header
@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


# This is returned when a FRESH TOKEN is EXPECTED and a NON FRESH TOKEN WAS SUPPLIED
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


# This is returned when a revoked token(token that has been added to blacklist) is being used from the header
@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# JWT configuration ends


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
# api.add_resource(UserConfirm, "/user_confirm/<int:user_id>")
api.add_resource(Confirmation, "/user_confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")
api.add_resource(GithubLogin, "/login/github")
# api.add_resource(GithubAuthorize, "/login/github/authorized")
api.add_resource(
    GithubAuthorize, "/login/github/authorized", endpoint="github.authorize"
)
api.add_resource(SetPassword, "/user/password")
api.add_resource(Order, "/order")

if __name__ == "__main__":
    db.init_app(app)
    # this tells the ma(Marshmallow object) what flask app it should be talking to
    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000)
