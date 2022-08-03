from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    fresh_jwt_required,
)
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema
from libs.strings import gettext


"""
Try as much as possible to use classmethod over static method as there is no difference over they are both 
called but more can be gotten from using class methon as it passes the cls as it's first argument anf it founds
application when using inheritance

The following resources contain endpoints that are protected by jwt,
one may need a valid access token, a valid fresh token or a valid token with authorized privilege 
to access each endpoint, details can be found in the README.md doc.  

fresh token = A token you have currently received after entering your username and password

non-fresh token = A token you received by refreshing a previous token
"""

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument(
    #     # "price", type=float, required=True, help="This field cannot be left blank!"
    #     "price", type=float, required=True, help=gettext("item_blank_error").format("price")
    # )
    # parser.add_argument(
    #     # "store_id", type=int, required=True, help="Every item needs a store_id."
    #     "store_id", type=int, required=True, help=gettext("item_blank_error").format("store_id")
    # )

    # note that @jwt_required is used instead of usual @jwt_required() when imported from flask_jwt_extended
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            # return item.json()
            return item_schema.dump(item), 200
        # return {"message": "Item not found"}, 404
        return {"message": gettext("item_not_found")}, 404

    # this will only run provided that the token is fresh i.e the user provided it's username and password
    # meaning we can not create a new item except we just log in
    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return (
                # {"message": "An item with name '{}' already exists.".format(name)},
                {"message": gettext("item_name_exists").format(name)},
                400,
            )

        # data = cls.parser.parse_args()
        # item = ItemModel(name, **data)

        item_json = request.get_json()
        item_json["name"] = name

        # try:
        #     item = item_schema.load(item_json)
        # except ValidationError as err:
        #     return err.messages, 400

        # # the above error handling has been done globally in app.py
        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": gettext("item_error_inserting")}, 500

        # return item.json(), 201
        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        # claims is used here for access level control, which is shown below
        # to give access to only admins, and paid user
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": gettext("admin_previlege_required")}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": gettext("item_deleted")}
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    def put(cls, name: str):
        # data = cls.parser.parse_args()

        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            # item.price = data["price"]
            item.price = item_json["price"]
        else:
            # item = ItemModel(name, **data)
            item_json["name"] = name

            # try:
            #     item = item_schema.load(item_json)
            # except ValidationError as err:
            #     return err.messages, 400

            # # the above error handling has been done globally in app.py
            item = item_schema.load(item_json)

        item.save_to_db()

        # return item.json()
        return item_schema.dump(item), 200


""""
.find_all() is used over .query.all() as these encapsulates the database interaction in the model instead
of exposing it to the resource
while in the resource use .find_all() and define it in terms of .query.all() inside the model

jwt_optional finds application for instance when withholding some information from a user who is not logged in
it is optional
"""


class ItemList(Resource):
    @classmethod
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        # items = [item.json() for item in ItemModel.query.all()]
        # items = [item.json() for item in ItemModel.find_all()]
        # items = [item_schema.dump(item) for item in ItemModel.find_all()]
        items = item_list_schema.dump(ItemModel.find_all())
        if user_id:
            return {"items": items}, 200
        return (
            {
                "items": [item["name"] for item in items],
                "message": gettext("login_required"),
            },
            200,
        )
