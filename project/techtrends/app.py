import os
import sqlite3
from sqlite3.dbapi2 import connect
from typing import Any
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from flask.helpers import make_response
from flask.templating import render_template_string
from flask.wrappers import Request, Response
from flask.logging import default_handler
from werkzeug.exceptions import abort
from werkzeug.wrappers import response


# The number of database connection count
db_connection_count = 0


# Create custom logger object to create logs
logger = logging.getLogger('techtrends_logs')

log_format = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')

logger.setLevel(logging.DEBUG)
print(logging.getLevelName(logger.level))
if logging.getLevelName(logger.level) == 'INFO' or 'DEBUG':
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    stdout_handler.setLevel(logging.getLevelName(logger.level))
    logger.addHandler(stdout_handler)
else:
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(log_format)
    stderr_handler.setLevel(logging.getLevelName(logger.level))
    logger.addHandler(stderr_handler)
    
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    try:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        global db_connection_count 
        db_connection_count +=1
        return connection
    except:
        return make_response(jsonify({'message':'ERROR - Unhealthy'})),500

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
    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
        return render_template('index.html', posts=posts)
    except:
        return make_response(jsonify({'message':'ERROR - Unhealty'})),500
   
# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.error('No post is found.')
        return render_template('404.html'), 404
    else:
        logger.info(post['title']+' is accessed.')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About us page is accessed.')
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

            logger.info('New article \"'+title+'\" is created.')
            return redirect(url_for('index'))

    return render_template('create.html')

 
# Define the health status of application
@app.route('/healthz')
def healthz():    
    connection = get_db_connection()
    name = connection.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="posts" ').fetchone()
    if name == '' or name is None:
        return make_response(jsonify({'message':'ERROR - Unhealthy'})),500
    return make_response(jsonify({'message':'Ok - Healthy'})),200

# Define the metrics endpoint of application and return the updated amount of posts and number of connections made
# with the database
@app.route('/metrics')
def get_metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return make_response(jsonify({'Post Count':len(posts),'Numbers of database connection':db_connection_count})),200




# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
