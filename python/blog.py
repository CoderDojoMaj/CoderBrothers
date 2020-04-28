import os, jinja2
from python import logger

l = logger.get('BLOG')

def get_posts():
    posts = []
    for post_file in os.listdir('templates/posts'):
        with open(f'templates/posts/{post_file}') as f:
            try:
                t = jinja2.Template(f.read())
                ctx = t.new_context()
                title = next(t.blocks['title'](ctx)).strip()
                date = None
                author = None
                if 'author' in t.blocks:
                    author = next(t.blocks['author'](ctx)).strip()
                if 'date' in t.blocks:
                    date = next(t.blocks['date'](ctx)).strip()

                post = {'title': title, 'author': author, 'date': date}
                posts.append(post)
            except:
                l.error(f'ERROR WHILE LOADING POST {post_file}')
    return posts