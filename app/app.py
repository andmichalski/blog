import _sqlite3

from flask import Flask, request, g, render_template
from flask_misaka import Misaka
from flask_paginate import Pagination, get_page_parameter

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


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
@app.route('/blog')
def blog():
    search = False
    per_page = 5
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    cur = g.db.execute('select title, text from entries order by id desc')
    entries = []
    for row in cur.fetchall():
        title = row[0]
        if isinstance(row[1], bytes):
            text = row[1].decode('utf-8')
        else:
            text = row[1]
        entries.append(dict(title=title, text=text))
    page_entries = entries[(page - 1) * per_page:((page - 1) * per_page) + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(entries), search=search,
                            record_name='entry')
    return render_template('blog.html', entries=page_entries, pagination=pagination)


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == '__main__':
    app.run()
