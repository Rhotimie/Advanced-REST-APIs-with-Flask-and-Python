from marshmallow import Schema, fields, INCLUDE, EXCLUDE


class BookSchema(Schema):
    title = fields.Str()
    author = fields.Str()
    description = fields.Str()


incoming_book_data = {
    "title": "Clean Code",
    "author": "Bob Martin",
    "description": "A book about writing cleaner code, with examples in Java",
}

book_schema = BookSchema()
book = book_schema.load(incoming_book_data)

print(book)


class Book:
    def __init__(self, title, author, description):
        self.title = title
        self.author = author
        self.description = description


book_obj = Book(**book)


"""
The below would still work because description is not a required field
"""

# class BookSchema(Schema):
#     title = fields.Str()
#     author = fields.Str()
#     description = fields.Str()


# incoming_book_data = {
#     "title": "Clean Code",
#     "author": "Bob Martin",
# }

# book_schema = BookSchema()
# book = book_schema.load(incoming_book_data)

# print(book)


"""
The below would not work because description is a required field
"""


# class BookSchema(Schema):
#     title = fields.Str()
#     author = fields.Str()
#     description = fields.Str(required=True)

# incoming_book_data = {
#     "title": "Clean Code",
#     "author": "Bob Martin"
# }

# book_schema = BookSchema()
# book = book_schema.load(incoming_book_data)

# print(book)


"""
INCLUDE returns all the key-value pairs in the dictionary even if it is not specified in the schema
EXCLUDE returns only the key-value pairs in the dictionary that are specified in the schema
"""


# class BookSchema(Schema):
#     title = fields.Str()
#     author = fields.Str()


# incoming_book_data = {
#     "title": "Clean Code",
#     "author": "Bob Martin",
#     "description": "A book about writing cleaner code, with examples in Java"
# }


# book_schema = BookSchema(unknown=INCLUDE)
# book = book_schema.load(incoming_book_data)

# print(book)

# book_schema = BookSchema(unknown=EXCLUDE)
# book = book_schema.load(incoming_book_data)

# print(book)
