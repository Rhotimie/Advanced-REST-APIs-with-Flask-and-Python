from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

"""
There won't be an image model because the images will save to a file system and not database for now
we will only be using the schema to validate if what we receive is an image and then save the image into the file 
system with our image helper
this schema is only validating and deserializing the data image i.e incoming data to our application
we could do more by checking that the file format has a valid extension, accepted filename etc
"""

# creating a custom marshmallow fields for purpose of validation etc
# read up the documentation on creating custom fields using marshmallow
class FileStorageField(fields.Field):
    default_error_messages = {"invalid": "Not a valid image."}

    # this validation is only to verify and validate that the image exist
    def _deserialize(self, value, attr, data) -> FileStorage:
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            # this call the fail method of the current class inherited from fields.Field and return
            # default_error_messages
            self.fail("invalid")  # raises validation error

        return value


class ImageSchema(Schema):
    # this expects an image field in the data as soon as the schema loads the data while deserializing the field
    image = FileStorageField(required=True)
