import os
import jinja2
from python import logger, utils
from python.db import getDB

l = logger.get('BLOG')


def get_posts():
    posts = []
    for post in getDB().getPosts():
        date = post['date']
        post['date'] = utils.formatPostDate(date)
        posts.append(post)
    return posts

def get_posts_paged(page, posts_per_page):
    posts = []
    for post in getDB().getPostsPaged(page, posts_per_page):
        date = post['date']
        post['date'] = utils.formatPostDate(date)
        posts.append(post)
    return posts

def search_posts_paged(search, page, posts_per_page):
    posts = []
    for post in getDB().searchPostsPaged(search, page, posts_per_page):
        date = post['date']
        post['date'] = utils.formatPostDate(date)
        posts.append(post)
    return posts


def getPostTemplate(uuid):
    post = getDB().getPost(uuid)
    # l.info((post['title'], post['author'], post['date'], post['content']))
    # l.info('''[%s %s %s %s]''' % (post['title'], post['author'], post['date'], post['content']))
    template = '''{%% extends "post.html" %%}
	{%% block title %%} %s {%% endblock %%}
	{%% block author %%} %s {%% endblock %%}
	{%% block date %%} %s {%% endblock %%}
	{%% block markdown %%} %s {%% endblock %%}''' % (post['title'], post['author'], post['date'], post['content'])
    # l.info(template)
    return template
