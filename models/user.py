from typing import Dict, List, Union
from db import db
from requests import Response
from flask import request, url_for
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel

# UserJSON = Dict[str, Union[int, str]]


class UserModel(db.Model):
    __tablename__ = "users"

    # # nullable=False, is used to cover up for required=True in our Schema
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=True)
    DOB = db.Column(db.DateTime, nullable=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    # default="ogo-oluwa street" will populate the database with the default for user post request
    Address = db.Column(db.Text, nullable=True)
    # activated = db.Column(db.Boolean, default=False)
    """
    lazy="dynamic" means when we access the property, the database is queried, otherwise the value is loaded when the
            model is created
        means when a new user model is created, the confirmation is not retrievable from the database
        when we access the confirmation property, it then goes into the database to retrieve it
        it allows the ConfirmationModel(..) object to be created after UserModel(..) model
    cascade="all, delete-orphan" means whenever a user is deleted, it goes into the confirmations to delete all
        confirmations associated with the user
    """
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    """
    we don't need the code below to create class instance again with nullable=False set, as SQLalchemy
    uses the non nullable fields to define init method backend
    """
    # def __init__(self, username: str, password: str):
    #     self.username = username
    #     self.password = password

    # # def json(self) -> Dict:
    # def json(self) -> UserJSON:
    #     return {"id": self.id, "username": self.username}

    # the property below is required when a user has multiple confirmations, to get the most recent one which
    # is presumably less likely to be expired when some of the confirmations has expired
    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        # ordered by expiration time (in descending order)
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        # def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        # def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    # A response is just something that another API gives us
    def send_confirmation_email(self) -> Response:
        # calculating the link that we want our users to click in that email
        # string[:-1] means copying from start (inclusive) to the last index (exclusive), a more detailed link below:
        # from `http://127.0.0.1:5000/` to `http://127.0.0.1:5000`, since the url_for() would also contain a `/`
        # url_for() calculates the address/routes for a particular resource in flask
        # link = "http://127.0.0.1:5000/user_confirm/1"
        # https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation

        subject = "Registration Confirmation"
        # link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        # # new_link = "http://127.0.0.1:5000/user_confirm/uuid(e.g 7g8hhhagahaj87ahafy7)"
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"
        return Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
