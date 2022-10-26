import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


count=0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global count
    
    connection = sqlite3.connect('database.db')
    count = count + 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info(f"The 'Home page' page is retrieved successfully!")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(f"Article with '{post_id}' doesn't exist!")
      return render_template('404.html'), 404
    else:
      app.logger.info(f"Article '{post['title']}' is retrieved successfully!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f"The 'About Us' page is retrieved successfully!")
    return render_template('about.html')

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
            app.logger.info(f"The article '{title}' is created successfully!")

            return redirect(url_for('index'))

    app.logger.info(f"Failed attempt to create post!")

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    message = "OK - healthy"
    try:
        get_db_connection()
        return {'resutls': message}, 200
    except Exception as ex:
        message = 'ERROR - unhealthy'
        app.logger.exception(ex)
        return {'results': message}, 500


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(1) as total FROM posts').fetchone()["total"]
    connection.close()
    app.logger.info('Metrics are retrived successfully!')
    return { "db_connection_count": count, "post_count": json.dumps(post_count) }, 200

# start the application on port 3111
if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler =  logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = '%(levelname)s:%(name)s:%(asctime)s, %(message)s'
    datefmt = '%d/%m/%Y, %H:%M:%S'
    logging.basicConfig(format=format_output, datefmt=datefmt,level=logging.DEBUG, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')