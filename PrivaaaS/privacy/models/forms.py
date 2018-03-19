# -*- coding: utf-8 -*-
import json
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime, Numeric, Text, Unicode, UnicodeText
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators, \
    ValidationError, SubmitField
from wtforms.validators import DataRequired


make_translatable(options={'locales': ['pt', 'en', 'es'],
                           'auto_create_locales': True,
                           'fallback_locale': 'en'})

db = SQLAlchemy ()

class LoginForm (FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    remember_me = BooleanField("remember_me")


class Entradas (FlaskForm):
    sua_resposta = StringField("sua_resposta")


class DataSet_PolicyForm(FlaskForm):
    policy_file_name = StringField('policy_name', [validators.Length(min=4, max=255)])
    dataset_name = StringField('dataset_name', [validators.Length(min=4, max=255)])
    submit = SubmitField("Send")
