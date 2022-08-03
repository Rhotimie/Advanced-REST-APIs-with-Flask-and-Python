import os
from flask import g
from flask_oauthlib.client import OAuth

"""
This consists of the client's settings
client is the API we are interacting with
just as we are client to the user, twitter/facebook/instagram is also a client to us
oauth object is the link between the settings we create here and our app
os.getenv() is the same thing as os.env.get()
request_token_url is dependent on whether the provider is using OAuth1 or OAuth2
    for OAuth2, it has to be None
authorize_url is where we send the user to, to authorize us(takes in code, client_id, client_secret)
authorize_url is where we send the data to after the user has authorize us to get access token(takes in client_id e.t.c)
"""
oauth = OAuth()

github = oauth.remote_app(
    "github",
    consumer_key=os.getenv("GITHUB_CONSUMER_KEY"),
    consumer_secret=os.getenv("GITHUB_CONSUMER_SECRET"),
    request_token_params={"scope": "user:email"},
    base_url="https://api.github.com/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
)

# token getsetter
@github.tokengetter
def get_github_token():
    if "access_token" in g:
        return g.access_token
