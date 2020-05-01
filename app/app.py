import functools

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_misaka import Misaka
from flask_paginate import Pagination, get_page_parameter

import _sqlite3

app = Flask(__name__)
app.config.from_object('config.LocalConfig')

Misaka(app, fenced_code=True)

STATIC_WEBSITES = ["power_curve_btwin_inride_100"]


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def connect_db():
    return _sqlite3.connect(app.config['DATABASE'])


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner


@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # if password == app.config['ADMIN_PASSWORD']:
        if password == 'secret':
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('manage'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('about'))


@app.route('/manage')
@login_required
def manage():
    data = g.db.execute(
        'select title, slug from entries order by id desc')
    entries = []
    for row in data.fetchall():
        title = row[0]
        slug = row[1]
        entries.append(dict(title=title, slug=slug))
    return render_template('manage.html', entries=entries)


@app.route("/")
def about():
    return render_template("about.html")


@app.route('/blog')
def blog():
    search = False
    per_page = 5
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    cur = g.db.execute(
        'select title, slug, text from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        title = row[0]
        slug = row[1]
        if isinstance(row[2], bytes):
            text = row[2].decode('utf-8')
        else:
            text = row[2]
        entries.append(dict(title=title, slug=slug, text=text))
    page_entries = entries[(page - 1) *
                           per_page:((page - 1) * per_page) + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(entries), search=search,
                            record_name='entry')
    return render_template('blog.html', entries=page_entries, pagination=pagination)


@app.route('/<slug>/')
def detail(slug):
    if slug in STATIC_WEBSITES:
        url = f"{slug}.html"
        return render_template(url)
    else:
        cur = g.db.execute(f'select title, text from entries where slug="{slug}"')
        entry_data = cur.fetchall()

        title = entry_data[0][0]
        text = entry_data[0][1].decode('utf-8')

        entry = {"title": title, "text": text}

        return render_template('detail.html', entry=entry)


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


def add_post(template, entry):
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('text'):

            title = request.form['title']
            slug = request.form['slug']
            text = request.form['text']
            published = request.form.get('published') or False
            # Add published value

            entry = {"title": title, "slug": slug,
                     "text": text, "published": published}

            post_exist = g.db.execute(f'select slug from entries where slug="{slug}"')
            record = post_exist.fetchall()
            if record != []:
                g.db.execute(f'update entries set title="{title}", slug="{slug}", text="{text}" where slug="{slug}"')
                g.db.commit()
            else:
                g.db.execute(f'insert into entries (title, slug, text) values ("{title}", "{slug}", "{text}")')
                g.db.commit()
            return redirect(url_for('manage'))
        else:
            flash('Title and Content are required.', 'danger')
    return render_template(template, entry=entry)


@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return add_post('create.html', {'title': '', 'slug': '', 'text': ''})


@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):

    record = g.db.execute(f'select title, text from entries where slug="{slug}"')
    entry_data = record.fetchall()

    title = entry_data[0][0]
    text = '\n' + entry_data[0][1]
    return add_post('edit.html', {'title': title, 'slug': slug, 'text': text})


@app.route('/<slug>/delete/', methods=['GET', 'POST'])
@login_required
def delete(slug):
    g.db.execute(f'delete from entries where slug = "{slug}"')
    g.db.commit()
    return redirect(url_for('manage'))


if __name__ == '__main__':
    app.run()
