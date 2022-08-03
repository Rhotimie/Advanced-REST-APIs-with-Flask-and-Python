from flask import request, render_template, make_response, redirect, g
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
import traceback

# bracket is required for multi line import
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    fresh_jwt_required,
)
from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST
from marshmallow import ValidationError
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel
from libs.strings import gettext
from libs.test_flask_lib import function_accessing_global


USER_LOGGED_OUT = "User <id={user_id}> successfully logged out."
# USER_LOGGED_OUT = "User <id={}> successfully logged out."


# _user_parser = reqparse.RequestParser()
# _user_parser.add_argument(
#     # "username", type=str, required=True, help="This field cannot be blank."
#     "username", type=str, required=True, help=gettext("user_blank_error").format("username")
# )
# _user_parser.add_argument(
#     # "password", type=str, required=True, help="This field cannot be blank."
#     "password", type=str, required=True, help=gettext("user_blank_error").format("password")
# )


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        # data = _user_parser.parse_args()

        # # using marshmallow library begat the code below
        # try:
        #     user_data = user_schema.load(request.get_json())    # creates dictionary
        # except ValidationError as err:
        #     return err.messages, 400

        # # using flask marshmallow library begat the code below
        # try:
        #     user= user_schema.load(request.get_json())             # creates class object
        # except ValidationError as err:
        #     return err.messages, 400

        # # the above error handling has been done globally in app.py
        # creates class object
        user = user_schema.load(request.get_json())

        # if UserModel.find_by_username(data["username"]):
        # if UserModel.find_by_username(user_data["username"]):
        if UserModel.find_by_username(user.username):
            return {"message": gettext("user_username_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": gettext("user_email_exists")}, 400

        # user = UserModel(data["username"], data["password"])
        # user = UserModel(**user_data)
        # user.save_to_db()

        # return {"message": gettext("user_created_successfully")}, 201

        try:
            user.password = generate_password_hash(user.password)
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, 201
        except MailGunException as e:
            user.delete_from_db()  # rollback
            # return {"message": e.message}, 500
            return {"message": str(e)}, 500
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback if confirmation.save_to_db() fails
            return {"message": gettext("user_error_creating")}, 500


# This is doing what the authenticate() function inside security.py is doing with different library(JWTManager)
class UserLogin(Resource):
    @classmethod
    def post(cls):
        # data = _user_parser.parse_args()

        # # using marshmallow library begat the code below
        # try:
        #     user_json = request.get_json()
        #     user_data = user_schema.load(user_json)
        # except ValidationError as err:
        #     return err.messages, 400

        # # using flask marshmallow library begat the code below
        # try:
        #     user_json = request.get_json()
        #     user_data = user_schema.load(user_json)
        # except ValidationError as err:
        #     return err.messages, 400

        # # the above error handling has been done globally in app.py
        user_json = request.get_json()
        # user_data = user_schema.load(user_json)
        user_data = user_schema.load(user_json, partial=("email",))

        # user = UserModel.find_by_username(data["username"])
        # user = UserModel.find_by_username(user_data["username"])
        user = UserModel.find_by_username(user_data.username)

        # # This is what the authenticate() function used to do
        if not user.password:
            return {"message": gettext("github_login")}, 400
        # if user and safe_str_cmp(user.password, data["password"]):
        if user and check_password_hash(user.password, user_data.password):
            # if user and safe_str_cmp(user_data.password, user.password):
            # This is what the identity() function used to do
            # if user.activated:
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                # global variable
                g.token = access_token
                function_accessing_global()

                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    200,
                )
            return {"message": gettext("user_not_confirmed").format(user.username)}, 400

        # return {"message": "Invalid Credentials!"}, 401
        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        # # we could have used user_id = get_jwt_identity() had it been we are to blacklist a user by its id
        user_id = get_jwt_identity()
        # BLACKLIST.add(user_id)
        jti = get_raw_jwt()["jti"]  # jti(JWT ID) is a raw token unique identifier
        BLACKLIST.add(jti)
        # return {"message": gettext("user_logged_out").format(jti)}, 200
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            # return {"message": "User Not Found"}, 404
            return {"message": gettext("user_not_found")}, 404
        # return user.json(), 200
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            # return {"message": "User Not Found"}, 404
            return {"message": gettext("user_not_found")}, 404
        user.delete_from_db()
        # return {"message": "User deleted."}, 200
        return {"message": gettext("user_deleted")}, 200


# here, the refresh token is supplied to the "TokenRefresh()" resource to create a non-fresh access token
# this allows for new token to be generated without asking the user for his/her username and password
class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


# # adding confirmed resource to manually confirmed user and try out this activated property
# class UserConfirm(Resource):
#     @classmethod
#     def get(cls, user_id: int):
#         user = UserModel.find_by_id(user_id)
#         if not user:
#             return {"message": gettext("user_not_found")}, 404

#         user.activated = True
#         user.save_to_db()
#         #  return {"message": gettext("user_confirmed")}, 200
#         # the below code redirect users from the url of this resource into another url/web application
#         # code=302 is for a temporary redirect
#         # return redirect("http://localhost:3000/", code=302)  # redirect if we have a separate web app
#         headers = {
#             "Content-Type": "text/html"
#         }  # this tells the browser that the content its receiving is html and json
#         return make_response(
#             # render_template("confirmation_page.html",
#             #                 email=user.username), 200, headers
#             render_template("confirmation_page.html", email=user.email),
#             200,
#             headers,
#         )


# This is used for changing password
class SetPassword(Resource):
    @classmethod
    @fresh_jwt_required
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)
        user = UserModel.find_by_username(user_data.username)

        if not user:
            return {"message": gettext("user_not_found")}, 400

        user.password = generate_password_hash(user_data.password)
        user.save_to_db()

        return {"message": gettext("user_password_updated")}, 201
