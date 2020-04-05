# -*- coding: utf-8 -*-
import flaskblog.creds as creds


class Config:
    SECRET_KEY = creds.secret_key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = creds.test_email_acc["smtp_server"]
    MAIL_PORT = creds.test_email_acc["smtp_port"]
    MAIL_USE_TLS = True
    MAIL_USERNAME = creds.test_email_acc["username"]
    MAIL_USERNAME = creds.test_email_acc["password"]
