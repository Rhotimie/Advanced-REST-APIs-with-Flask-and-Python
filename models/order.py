import os
import stripe

from db import db
from typing import List

CURRENCY = "usd"

# # this can not help us add a quantity of items to our relationship like [1, 1] or [2, 2] etc
# items_to_orders = db.Table(
#     "items_to_orders",
#     db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
#     db.Column("order_id", db.Integer, db.ForeignKey("orders.id"))
# )


# Association object pattern which is slightly modified many-to-many relationship through defining a secondary model
# so we now have Items --> ItemsInOrder(many-to-one) and orders --> ItemsInOrder(many-to-one) thus many-to-many
# relationship with a secondary model(allows for more columns for more data) in the middle
# we no longer have self.items again but self.items[0...x].item
# we can use these for items and store if we want an item to be part of many store
class ItemsInOrder(db.Model):
    __tablename__ = "items_in_order"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    # quantity is the number of items in an order
    quantity = db.Column(db.Integer)

    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)

    """
    we are doing this to make the order linked to a bunch of itens but the items will not know that they are linked 
    to that order using many-to-many relationship meaning one item can have many orders and one order and one order
    can have many items
    but items and store are linked by many-to-one relationship
    """
    # # this can not help us add a quantity of items to our relationship like [1, 1] or [2, 2] etc
    # items = db.relationship("ItemModel", secondary=items_to_orders, lazy="dynamic")

    # backref is an advance of back_populated, it will be reference only once if used
    items = db.relationship("ItemsInOrder", back_populates="order")

    @property
    def description(self) -> str:
        """
        Generates a simple string representing this order, in the format of "5x chair, 2x table"
        """
        item_counts = [
            f"{item_data.quantity}x {item_data.item.name}" for item_data in self.items
        ]
        return ",".join(item_counts)

    @property
    def amount(self) -> int:
        """
        Calculates the total amount to charge for this order.
        Assumes item price is in USD–multi-currency becomes much tricker!
        :return int: total amount of cents to be charged in this order.x`
        """
        return int(
            sum([item_data.item.price * item_data.quantity for item_data in self.items])
            * 100
        )

    @classmethod
    def find_all(cls) -> List["OrderModel"]:
        return cls.query.all()

    @classmethod
    def find_by_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()

    def charge_with_stripe(self, token: str) -> stripe.Charge:
        # Set your secret key: remember to change this to your live secret key in production

        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        return stripe.Charge.create(
            amount=self.amount,  # amount in us dollar cent/nigerian kobo we want to charge
            currency=CURRENCY,
            description=self.description,
            source=token,
        )

    def set_status(self, new_status: str) -> None:
        """
        Sets the new status for the order and saves to the database—so that an order is never not committed to disk.
        :param new_status: the new status for this order to be saved.
        """
        self.status = new_status
        self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
