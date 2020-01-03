import _sqlite3

from flask import Flask, request, g, render_template
from flask_misaka import Misaka
from flask_paginate import Pagination, get_page_parameter
import config

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

Misaka(app, fenced_code=True)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def connect_db():
    return _sqlite3.connect(app.config['DATABASE'])


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

    cur = g.db.execute('select title, slug, text from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        title = row[0]
        slug = row[1]
        if isinstance(row[2], bytes):
            text = row[2].decode('utf-8')
        else:
            text = row[2]
        entries.append(dict(title=title, slug=slug, text=text))
    page_entries = entries[(page - 1) * per_page:((page - 1) * per_page) + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(entries), search=search,
                            record_name='entry')
    return render_template('blog.html', entries=page_entries, pagination=pagination)

@app.route('/<slug>/')
def detail(slug):
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

@app.route("/power_curve")
def power_curve():
    return render_template("power_curve.html")

if __name__ == '__main__':
    app.run()

