from typing import Dict, List, Union
from db import db
from models.item import ItemJSON

# StoreJSON = Dict[str, Union[int, str, List[ItemJSON]]]


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

    items = db.relationship("ItemModel", lazy="dynamic")

    # def __init__(self, name: str):
    #     self.name = name

    # # def json(self) -> Dict:
    # def json(self) -> StoreJSON:
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "items": [item.json() for item in self.items.all()],
    #     }

    @classmethod
    def find_by_name(cls, name: str) -> "StoreModel":
        # def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        # def find_all(cls) ->List:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
