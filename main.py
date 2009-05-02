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
from models import countusers
from models import get_tuser_count
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
        tuser = Tuser(uid="9581222",
                      name="suztomo",
                      profile_image="http://s3.amazonaws.com/twitter_production/profile_images/85734855/mari_normal.png",
                      priority=1)
        debug('Hello')
        tuser.putfav()
        self.response.out.write('hogehoge')



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
