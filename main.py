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


APP_DIRECTORY = dirname(__file__)
sys.path.insert(0, join_path(APP_DIRECTORY, 'third_party'))

import feedparser

from models import Tuser
from models import get_tuser_count
from models import users_to_fav
from delete_handler import DeleteAllUsersHandler
from updateuser_handler import UpdateUserFavotter
from updateuser_handler import UpdateUserTwitterSearch

def debug(msg):
    pass
#    logging.getLogger().debug(msg)



class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello Favotter! %d' % get_tuser_count())

class UpdateFavHandler(webapp.RequestHandler):
    def get(self):
        debug("putfav_mae")
        tusers = users_to_fav()
        fav_count = 0
        for tuser in tusers:
            fav_count = fav_count + tuser.putfav()
        self.response.out.write('New %d favs' % fav_count)



def main():
    application = webapp.WSGIApplication(
        [
            ('/', MainHandler),
            ('/updatefav', UpdateFavHandler),
            ('/updateuser', UpdateUserTwitterSearch),
            ('/updateuserfavotter', UpdateUserFavotter),
            ('/deletealluser', DeleteAllUsersHandler)
         ],
        debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
