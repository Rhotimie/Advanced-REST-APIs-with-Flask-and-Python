# from marshmallow import Schema, fields
from marshmallow import pre_dump
from ma import ma
from models.user import UserModel

# # using marshmallow library begat the code below
# class UserSchema(Schema):
#     class Meta:
#         load_only = ("password",)
#         dump_only = ("id",)

#     id = fields.Int()
#     username = fields.Str(required=True)
#     password = fields.Str(required=True)


# # using flask marshmallow library begat the code below
class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "confirmation")

        # this will help return a user with most recent confirmation and not all confirmations
        # the user we are passing into the below function is the one we are about to convert to json
        @pre_dump
        def _pre_dump(self, user: UserModel):
            user.confirmation = [user.most_recent_confirmation]
            return user
