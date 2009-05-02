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

from os.path import dirname, join as join_path

import wsgiref.handlers
import re


from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template


APP_DIRECTORY = dirname(__file__)
sys.path.insert(0, join_path(APP_DIRECTORY, 'third_party'))

import feedparser

from models import Tuser
from models import recentTuser
from models import countusers
from models import users_dict_by_names
from models import add_tuser_counter
from delete_handler import DeleteAllUsersHandler

TWITTER_SEARCH_FORMAT =  "http://search.twitter.com/search.atom?q=%s"
FAVOTTER_FEED = "http://favotter.matope.com/rss.php?mode=new"
GQL_QUERY_IN_MAX = 30

def debug(msg):
    pass
#    logging.getLogger().debug(msg)


class UpdateUserFavotter(webapp.RequestHandler):
    """Update Tuser using favotter.matope.com
    """
    def get(self):
        """update user info using favotter.
        """
        fav_by_regex = re.compile('twitter.com/(?P<username>[^"]+)')
        icon_regex = re.compile('src="(?P<icon_image>[^"]+)')
        feed = feedparser.parse(FAVOTTER_FEED)
        users_feed_dict = {}
        today = datetime.now()
        dummy_last_crawl = today + timedelta(weeks=-4)
        users_feed_dict = {}
        found_users_count = 0
        for entry in feed.entries:
            start_index = entry.summary.find('fav by')
            if (start_index < 0):
                continue
            fav_by_string = entry.summary[start_index:]
            debug(fav_by_string)
            username_list = fav_by_regex.findall(fav_by_string)
            icon_url_list = icon_regex.findall(fav_by_string)

            if len(username_list) != len(icon_url_list):
                debug("length mismatch")
                debug(username_list)
                debug(icon_url_list)
                debug(fav_by_string)
                continue

            debug(len(username_list))
            for i in range(len(username_list)):
                author = username_list[i]
                icon_url = icon_url_list[i]
                if author in users_feed_dict:
                    continue
                if found_users_count >= GQL_QUERY_IN_MAX:
                    break
                user_info_dict = {
                    'uid' : '0',
                    'name' : author,
                    'profile_image' : icon_url,
                    'last_crawl' : dummy_last_crawl
                    }
                users_feed_dict[author] = user_info_dict
                found_users_count = found_users_count + 1

        db_users_dict = users_dict_by_names(users_feed_dict.keys())
        users_to_put = []
        added_user_count = 0
        for user_name in users_feed_dict.keys():
            debug(user_name)
            # Do not save existing user
            if user_name in db_users_dict:
                debug("%s is already in db" % user_name)
                continue
            tuser = Tuser(
                uid="0",
                name=user_name,
                profile_image=users_feed_dict[user_name]['profile_image'],
                last_crawl=users_feed_dict[user_name]['last_crawl'],
                priority=1
                )
            debug(users_feed_dict[user_name])
            users_to_put.append(tuser)
            added_user_count = added_user_count + 1
        db.put(users_to_put)
        add_tuser_counter(added_user_count)
        self.response.out.write('added new %d users' % added_user_count)




class UpdateUserTwitterSearch(webapp.RequestHandler):
    """UpdateTuser using twitter search
    """
    def get(self):
        search_keyword = self.request.get('q')
        recent_user_url =TWITTER_SEARCH_FORMAT % search_keyword
        feed = feedparser.parse(recent_user_url)
        last_user = recentTuser()
        users_feed_dict = {}
        last_user_created = last_user.created if last_user else  None
        for entry in feed.entries:
            icon_url = entry.links[1]['href']
            # Skip if the result is already crawled.
            entry_datetime = datetime(*(entry.updated_parsed[:6]))
            if last_user_created and entry_datetime <= last_user_created:
#                debug("%s is older than %s" % (entry_datetime, last_user_created))
                continue
            if 'href' in entry and entry.href.find('http://twitter.com/') == 0:
                author = entry.href[len('http://twitter.com/'):]
            else:
                continue
            dummy_last_crawl = entry_datetime + timedelta(weeks=-4)
            user_info_dict = {
                'uid' : '0',
                'name' : author,
                'profile_image' : icon_url,
                'last_crawl' : dummy_last_crawl
                }
            users_feed_dict[author] = user_info_dict

        db_users_dict = users_dict_by_names(users_feed_dict.keys())
        users_to_put = []
        for user_name in users_feed_dict.keys():
            if user_name in db_users_dict:
                debug("%s is already in db" % user_name)
                continue
            tuser = Tuser(
                uid="0",
                name=user_name,
                profile_image=users_feed_dict[user_name]['profile_image'],
                last_crawl=users_feed_dict[user_name]['last_crawl'],
                priority=1
                )
            users_to_put.append(tuser)
        db.put(users_to_put)
        self.response.out.write('added new %d users' % len(users_feed_dict.keys()))

