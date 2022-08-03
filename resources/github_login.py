from flask import g, request, url_for
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token

from oa import github
from schemas.user import UserSchema
from models.user import UserModel
from models.confirmation import ConfirmationModel

user_schema = UserSchema()

"""
callback is when we want to go when the user has been authorized
this resource can only be accessed on the browser and not POSTMAN
http://localhost:5000/login/github
"""


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        # return github.authorize(callback="http://localhost:5000/login/github/authorized")
        """
        url_for("github.authorize", _external=True) is used to use any domain we decide to use rather than hardcoding 
        this. And because we are in a request context, we know the url that the used in getting here
        _external=True means that wewant to build the full URL and not just the URL for internal use
        URL for internal use: /login/github/authorized
        External URL = http://localhost:5000/login/github/authorized
        It finds application also in situations where we deployed on multiple server
        """
        return github.authorize(callback=url_for("github.authorize", _external=True))


# when users gives us authorization to use their data, this resource is sent to github to get the user's access token
# Get authorization
# Create user
# Save github token to user
# Create access token
# Return JWT
# Tokengetter will then use the current user to load token from database
class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        resp = github.authorized_response()
        if resp is None or resp.get("access_token") is None:
            error_response = {
                "error": request.args["error"],
                "error_description": request.args["error_description"],
            }
            return error_response

        g.access_token = resp["access_token"]
        # this uses the access_token from the tokengetter function and keeps the Oauth configuration inside one file
        github_user = github.get("user")
        # github_user = github.get('user', token=g.access_token)
        github_username = github_user.data["login"]
        # return github_username

        user = UserModel.query.filter_by(username=github_username).first()

        if not user:
            user = UserModel(username=github_username)
            user.save_to_db()

            _user = UserModel.query.filter_by(username=github_username).first()
            confirmation = ConfirmationModel(_user.id)
            confirmation.confirmed = True
            confirmation.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}, 200
