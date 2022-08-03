"""
blacklist.py
This allows us to have a list of things that we don't want give access to like users id, tokens e.t.c

This file just contains the list of JWT tokens that have been revoked through logging out 
it will be imported by app and used by logout resource so that tokens unique id can be added to the blacklist 
when the user logs out.
"""

# BLACKLIST = {2, 3}
BLACKLIST = set()
