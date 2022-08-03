import os
from typing import List
from requests import Response, post

# # Absolute import
from libs.strings import gettext

# # Relative import
# from .strings import gettext

# Error handling in Mailgun
class MailGunException(Exception):
    # takes in a message and call the super class init method with that message
    def __init__(self, message: str):
        super().__init__(message)


# creating our own mailgun library
class Mailgun:

    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", None)

    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = f"do-not-reply@{MAILGUN_DOMAIN}"

    @classmethod
    def send_email(
        cls, email: List[str], subject: str, text: str, html: str
    ) -> Response:

        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(gettext("mailgun_failed_load_api_key"))

        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(gettext("mailgun_failed_load_domain"))

        # # sending request to the mailgun API
        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )

        if response.status_code != 200:
            raise MailGunException(gettext("mailgun_error_send_email"))

        return response


"""
do "pip install python-dotenv" to work on .env files
.env(environment variable) is used to store secret details that you don't want to be embedded inside the code
.env.example is what we share on a version control system like github
so .env is added to .gitignore
"""
