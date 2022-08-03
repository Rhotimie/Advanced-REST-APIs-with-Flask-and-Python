from marshmallow import Schema, fields

"""
We are now beginning to use Marshmallow over reqparse because reqparse are beginning to be decapretated
Marshmallow is a library used for serialization and deserialization of data
Marshmallow is the new recommended way of serializing and deserializing data
  --it forces us to structure our code better
  --it helps with separating our models from our data interactions
  --It takes in object of classes, convert it into dictionary after dumping
"""


class BookSchema(Schema):
    title = fields.Str()
    author = fields.Str()


class Book:
    def __init__(self, title, author, description):
        self.title = title
        self.author = author
        self.description = description


book = Book("Clean Code", "Bob Martin", "A book about writting cleaner code")

book_schema = BookSchema()
book_dict = book_schema.dump(book)

print(book_dict)
