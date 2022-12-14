from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema
from libs.strings import gettext

NAME_ALREADY_EXISTS = "A store with name '{}' already exists."
ERROR_INSERTING = "An error occurred while inserting the store."
STORE_NOT_FOUND = "Store not found."
STORE_DELETED = "Store deleted."

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            # return store.json()
            return store_schema.dump(store), 200
        # return {"message": "Store not found"}, 404
        return {"message": gettext("store_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return (
                # {"message": "A store with name '{}' already exists.".format(name)},
                {"message": gettext("store_name_exists").format(name)},
                400,
            )

        # store = StoreModel(name)
        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            # return {"message": "An error occurred creating the store."}, 500
            return {"message": gettext("store_error_inserting")}, 500

        # return store.json(), 201
        return store_schema.dump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            # return {"message": "Store deleted"}, 200
            return {"message": gettext("store_deleted")}, 200

        return {"message": gettext("store_not_found")}, 404


""""
.find_all() is used over .query.all() as these encapsulates the database interaction in the model instead
of exposing it to the resource
while in the resource use .find_all() and define it in terms of .query.all() inside the model
"""


class StoreList(Resource):
    @classmethod
    def get(cls):
        # return {'stores': [store.json() for store in StoreModel.query.all()]}
        # return {"stores": [store.json() for store in StoreModel.find_all()]}
        return {"stores": store_list_schema.dump(StoreModel.find_all())}, 200
