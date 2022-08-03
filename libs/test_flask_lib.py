from flask import g

"""
FLASK G is similar to a global object that can be accessed anywhere in our flask App
    --used to share data between different parts of an application
    --for sharing data accross the application
    --g is useful for storing information about user making a request
    --g is useful for sharing data for use in multiple parts of the application
    CAVEATS OF G
        --It can only be used while inside a request context, meaning it can not be used inside app.py except if it is 
            set and used in a request context contained in app.py
        --g does not keep any of it's content between request, meaning every request has it's own g
        --g cannot be set in a request and be called in another request
    
"""


def function_accessing_global():
    print(g.token)
