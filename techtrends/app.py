import sqlite3
import logging
import os
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

def define_log_level():
    log_level = os.getenv("LOGLEVEL", "DEBUG")
    log_level = (
        getattr(logging, log_level.upper())
        if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )

    logging.basicConfig(format='[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['connection_count'] = app.config['connection_count'] + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    logging.debug("Post with ID '{0}' is retrieved.".format(post_id))
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['connection_count'] = 0

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    logging.debug("Main page with '{0}' articles is shown.".format(len(posts)))
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.error('A non-existing article is accessed!')
      return render_template('404.html'), 404
    else:
      logging.debug("Article with title '{0}' is retrieved!".format(post["title"]))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug('The "About Us" page is shown.')
    return render_template('about.html')
    
# Define healthz endpoint
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        return {"result": "OK - healthy"}, 200
    except Exception:
        return {"result": "ERROR - unhealthy"}, 500
    
# Define metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    data = {"db_connection_count": app.config['connection_count'], "post_count": len(posts)}
    return data

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.debug("Article with title '{0}' is created.".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')
   

# start the application on port 3111
if __name__ == "__main__":
   define_log_level()
   app.run(host='0.0.0.0', port='3111')
