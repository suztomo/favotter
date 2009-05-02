#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import os
import sys
import time
import logging
from datetime import datetime
from datetime import timedelta
from datetime import date

from os.path import dirname, join as join_path

import wsgiref.handlers


from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template

from models import Tuser
from models import delete50users

class DeleteAllUsersHandler(webapp.RequestHandler):
    def get(self):
        try:
            delete50users()
            self.response.out.write('ok')
        except Exception, e:
            self.response.out.write('miss')

