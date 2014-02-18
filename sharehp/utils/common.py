# -*- coding: utf-8 -*-
from datetime import datetime
from exceptions import ValueError
import uuid
import hashlib


def unique_filename():
    date_prefix = datetime.now().strftime('%Y%m%d')
    filename = str(uuid.uuid1()).replace('-', '')
    return date_prefix + '_' + filename


def unique_session_id():
    return str(uuid.uuid1()).replace('-', '')


def safe_int(val, default=0):
    try:
        val = int(val)
    except ValueError:
        val = default
    return val


def encode_password(password):
    return hashlib.md5(password).hexdigest()


