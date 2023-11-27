from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import torch

from datasets import load_dataset
from transformers import pipeline
from transformers import AutoModel, AutoTokenizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from umap import UMAP
#from flask_migrate import Migrate

app = Flask(__name__) # Initialize a Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # Configure the application to use SQLite database
db = SQLAlchemy(app) # Initialize SQLAlchemy with the Flask app
#migrate = Migrate(app, db) # Initialize Flask-Migrate with the Flask app and SQLAlchemy database

class Todo(db.Model): # Define a Todo model for the SQLAlchemy ORM
    id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
    content = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    #date_created = db.Column(db.DateTime, default=datetime.utcnow) # Define 'date_created' column with a default value of the current UTC time
    content_summary = db.Column(db.String(200), default="hi")#nullable=False) # instead of date_created, we will do a summary of the content

    def __repr__(self): # Representation method to display a task's ID
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET']) # Define the index route, which supports both POST and GET methods
def index():
    if request.method == 'POST': # If the method is POST, add a new task
        # MULTIPLE CHOICE QUESTION??        

        task_content = request.form['content'] # Retrieve the task content from the form data
        # retrieve the summary of the task content
        summarizer = pipeline("summarization") # load the model
        content_summary_from_model = summarizer(task_content, min_length=10, max_length=25,
           clean_up_tokenization_spaces=True)[0]['summary_text']
        new_task = Todo(content=task_content, content_summary=content_summary_from_model) # Create a new Todo object with the task content

        try:
            db.session.add(new_task) # Add the new task to the database session and commit
            db.session.commit()
            return redirect('/') # Redirect to the home page after adding the task
        except:
            return 'There was an issue adding your task' # Return an error message if there's an issue adding the task

    else: # If the method is GET, display current tasks
        #tasks = Todo.query.order_by(Todo.date_created).all() # Query the database for all tasks, ordered by creation date
        tasks = Todo.query.all()
        return render_template('index.html', tasks=tasks) # Render the index template with the list of tasks


@app.route('/delete/<int:id>') # Define the delete route for a task, identified by its id
def delete(id):
    task_to_delete = Todo.query.get_or_404(id) # Retrieve the task by id or return 404 if not found

    try:
        db.session.delete(task_to_delete) # Delete the task from the database and commit the change
        db.session.commit()
        return redirect('/') # Redirect to the home page after deletion
    except:
        return 'There was a problem deleting that task' # Return an error message if there's a problem deleting the task

@app.route('/update/<int:id>', methods=['GET', 'POST']) # Define the update route for a task, supporting both GET and POST methods
def update(id):
    task = Todo.query.get_or_404(id) # Retrieve the task by id or return 404 if not found

    if request.method == 'POST': # If the method is POST, update the task
        task.content = request.form['content'] # Update the task content with the form data
        # update the summary of the task content
        summarizer = pipeline("summarization")
        content_summary_from_model = summarizer(task.content, min_length=10, max_length=25,
           clean_up_tokenization_spaces=True)[0]['summary_text']
        task.content_summary = content_summary_from_model

        try:
            db.session.commit() # Commit the updates to the database
            return redirect('/') # Redirect to the home page after updating the task
        except:
            return 'There was an issue updating your task' # Return an error message if there's an issue updating the task

    else:
        return render_template('update.html', task=task, content_summary=content_summary_from_model) # If the method is GET, render the update template with the task data


if __name__ == "__main__": # Conditional to ensure the script runs only if it is the main program
    app.run(debug=True) # Run the Flask application with debug mode enabled
