#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from datetime import datetime
import feedparser

import logging

TWITTER_FAV_URL_FORMAT = "http://twitter.com/favorites/%s.rss"

def debug(msg):
    pass
#    logging.getLogger().debug(msg)

class Counter(db.Model):
    """Counter
    """
    name = db.StringProperty(verbose_name="counter name",
                                default="favotter")
    count = db.IntegerProperty(verbose_name="counter",
                               default=0)
    updated = db.DateTimeProperty(verbose_name="The time this row is updated",
                                  auto_now=True)
    created = db.DateTimeProperty(verbose_name="The time this row is created",
                                  auto_now_add=True)

def add_tuser_counter(num):
    counters_query = db.GqlQuery("SELECT * FROM Counter WHERE name = :1 LIMIT 1",
                                 "tuser")
    if counters_query.count() > 0:
        counter = counters_query[0]
    else:
        debug("created new counter")
        counter = Counter()
    counter.count = counter.count + num
    counter.put()

def get_tuser_count():
    counters_query = db.GqlQuery("SELECT * FROM TuserCount LIMIT 1")
    if counters_query.count() > 0:
        counter = counters_query[0]
    else:
        debug("created new counter")
        counter = Counter()
    return counter.count

def add_tweet_count(num):
    counters_query = db.GqlQuery("SELECT * FROM Counter WHERE name = :1 LIMIT 1",
                                 "tweet")
    if counters_query.count() > 0:
        counter = counters_query[0]
    else:
        debug("created new counter")
        counter = Counter(name="tweet")
    counter.count = counter.count + num
    counter.put()

def add_fav_count(num):
    counters_query = db.GqlQuery("SELECT * FROM Counter WHERE name = :1 LIMIT 1",
                                 "fav")
    if counters_query.count() > 0:
        counter = counters_query[0]
    else:
        debug("created new counter")
        counter = Counter(name="fav")
    counter.count = counter.count + num
    counter.put()

class Fav(db.Model):
    """A favorite"""
    tweet_url = db.StringProperty(verbose_name="tweet url (expressed in string)",
                            required=True)
    user_name = db.StringProperty(verbose_name="user name (expressed in string)",
                            required=True)

    updated = db.DateTimeProperty(verbose_name="The time this favorite is updated",
                                  auto_now=True)
    created = db.DateTimeProperty(verbose_name="The time this favorite is created",
                                  auto_now_add=True)

class Tuser(db.Model):
    """A user who want to crawl"""
    uid = db.StringProperty(verbose_name="user id (expressed in string)"
                            )
    name = db.StringProperty(verbose_name="The user's twitter account",
                             required=True)
    profile_image = db.LinkProperty(verbose_name="Link to the icon image",
                           required=True)

    priority = db.IntegerProperty(verbose_name="The priority of the user",
                                  default=1,
                                  required=True)
    last_crawl = db.DateTimeProperty(verbose_name="The last time the user crawled",
                                    required=True)
    updated = db.DateTimeProperty(verbose_name="The time this user is updated",
                                  auto_now=True)
    created = db.DateTimeProperty(verbose_name="The time this user is created",
                                  auto_now_add=True)

    def putfav(self):
        fav_feed_url = TWITTER_FAV_URL_FORMAT % self.name
        favorites = feedparser.parse(fav_feed_url)
        debug("putfav %d" % len(favorites.entries))
        fav_count = 0
        for favorite in favorites.entries:
            debug(favorite.title)
            fav_time = datetime(*(favorite.updated_parsed[:6]))
            # Pass old favorite
            if fav_time < self.last_crawl:
                continue
            tweet = Tweet(url=favorite.id,
                          text=favorite.title,
                          html_text=favorite.title)
            fav = Fav(tweet_url=favorite.id,
                      user_name=self.name)
            tweet.put()
            fav.put()
            fav_count = fav_count + 1
        self.last_crawl = datetime.now()
        self.put()
        return fav_count

class Tweet(db.Model):
    """A tweet"""
    url = db.StringProperty(verbose_name="tweet url (expressed in string)",
                            required=True)
    text = db.TextProperty(verbose_name="The tweet",
                           required=True)
    html_text = db.TextProperty(verbose_name="The tweet as html")
    created = db.DateTimeProperty(verbose_name="The time this tweet is created",
                                  auto_now_add=True)

class CrawlStatus(db.Model):
    favotter_crawl = db.DateTimeProperty(verbose_name="favotter crawled",
                                  auto_now=True)
    tsearch_crawl =  db.DateTimeProperty(verbose_name="twitter search crawled",
                                  auto_now=True)


def recentTuser():
    users = db.GqlQuery(
        "SELECT * FROM Tuser ORDER BY created DESC LIMIT 1"
        )
    for user in users:
        return user
    return None
#    return users[0] if users else None

def delete50users():
    q = db.GqlQuery("SELECT * FROM Tuser")
    results = q.fetch(1000)
    db.delete(results)

def countusers():
    q = db.GqlQuery("SELECT * FROM Tuser")
    return q.count()

def users_dict_by_names(names):
    users = db.GqlQuery("SELECT * FROM Tuser WHERE name IN :1", names)
    dic = {}
    for user in users:
        dic[user.name] = user
    return dic

def users_to_fav():
    users = db.GqlQuery("SELECT * FROM Tuser ORDER BY last_crawl ASC LIMIT 2")
    return users
