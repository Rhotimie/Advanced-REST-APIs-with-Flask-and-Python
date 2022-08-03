from typing import Dict, List, Union
from db import db

# adding custom json types
# the code below means all keys in the Dict are strings and it's values a union of int, str and float
ItemJSON = Dict[str, Union[int, str, float]]

"""
using BLACK formatter to format code is particularly more useful not to have different code formatting when 
working with many people and using a version control system like Git
"""


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True is to help ensure that only a unique item name exist inside the database
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel")

    # # adding type hinting, primitive types can be referenced without importing anything
    # # type hinting is just there to help the developer, it is ignored when the program runs
    # def __init__(self, name: str, price: float, store_id: int):
    #     self.name = name
    #     self.price = price
    #     self.store_id = store_id

    # # def json(self) -> Dict:
    # def json(self) -> ItemJSON:
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "price": self.price,
    #         "store_id": self.store_id,
    #     }

    """
    "ItemModel" return type helps to tell python that evaluate find_by_name(cls, name: str) after the current 
    file has been imported
    meaning this is the way python recommends returning self type
    """

    @classmethod
    def find_by_name(
        cls, name: str
    ) -> "ItemModel":  # returning the current class as a type
        # def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(
        cls, _id: int
    ) -> "ItemModel":  # returning the current class as a type
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["ItemModel"]:  # returning the current class as a type
        # def find_all(cls) -> List
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
