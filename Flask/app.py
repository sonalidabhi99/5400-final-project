from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

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
from flask_migrate import Migrate
from flask import session

app = Flask(__name__) # Initialize a Flask application
app.secret_key = 'super_secret_key' # Set a secret key for the application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # Configure the application to use SQLite database
db = SQLAlchemy(app) # Initialize SQLAlchemy with the Flask app
migrate = Migrate(app, db) # WHEN WE CHANGE THE DATABASE--UNCOMMENT THIS LINE ON THE FIRST RUN; Initialize Flask-Migrate with the Flask app and SQLAlchemy database

class Todo(db.Model): # Define a Todo model for the SQLAlchemy ORM
    id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
    content = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    #date_created = db.Column(db.DateTime, default=datetime.utcnow) # Define 'date_created' column with a default value of the current UTC time
    content_summary = db.Column(db.String(200), default="hi")#nullable=False) # instead of date_created, we will do a summary of the content

    def __repr__(self): # Representation method to display a task's ID
        return '<Task %r>' % self.id

class Law(db.Model): # Define a Todo model for the SQLAlchemy ORM
    id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
    law_title = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    law_text = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    location = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    type = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    keywords = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    def __repr__(self): # Representation method to display a task's ID
        return '<Task %r>' % self.id

class Output(db.Model): # Define a Todo model for the SQLAlchemy ORM
    id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
    law_titles_included = db.Column(db.String(200), default="no laws found") # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
    #date_created = db.Column(db.DateTime, default=datetime.utcnow) # Define 'date_created' column with a default value of the current UTC time
    laws_summary = db.Column(db.String(200), default="no laws to summarize")#nullable=False) # instead of date_created, we will do a summary of the content

    def __repr__(self): # Representation method to display a task's ID
        return '<Task %r>' % self.id

def load_data_from_csv(csv_filename):
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # Create a new Law object and populate its attributes from the CSV data
            law = Law(
                law_title=row['law_title'],
                law_text=row['law_text'],
                location=row['location'],
                type=row['Type'],
                keywords=row['Keywords']
            )
            # Add the law object to the database session and commit the changes
            db.session.add(law)
            db.session.commit()

@app.route('/', methods=['POST', 'GET']) # Define the index route, which supports both POST and GET methods
def index():
    # read in csv to dataframe
    df = pd.read_csv('../data/clean_data.csv')
    # create a list of keywords for the multiselect
    keywords_for_mult_select = []
    for k in df['Keywords']:
        if type(k) == float:
            continue
        # try:
        k = k.split(',')
        k = [x.strip() for x in k]
        # except:
        #     continue
        for l in k:
            # remove whitespace and non-alphanumeric characters
            l = l.strip()
            # make lowercase
            l = l.lower()
            #l = ''.join(e for e in l if e.isalnum())
            keywords_for_mult_select.append(l)
    keywords_for_mult_select = list(set(keywords_for_mult_select))
    keywords_for_mult_select.sort()
    locations_for_mult_select = ['VA', 'MD', 'DC']
    locations_for_mult_select.sort()

    #keywords_for_mult_select = ["keyword1", "keyword2", "keyword3"]
    if request.method == 'POST': # If the method is POST, add a new task
        # filter db for regex of selected options in keywords column--return list of laws
        from sqlalchemy import and_
        # Get the selected options and locations from the form
        selected_options = request.form.getlist('options')
        location_selected = request.form.getlist('location')
        task_content = request.form['content'] # Retrieve the task content from the form data
        # retrieve the summary of the task content
        summarizer = pipeline("summarization") # load the model
        content_summary_from_model = summarizer(task_content, min_length=10, max_length=25,
           clean_up_tokenization_spaces=True)[0]['summary_text']
        new_task = Todo(content=task_content, content_summary=content_summary_from_model) # Create a new Todo object with the task content
        # new_law_query = Output(law_titles_included=law_titles, laws_summary=laws) 
        session['content'] = task_content
        session['location'] = location_selected
        session['options'] = selected_options
        try:
            
            #db.session.add(new_task) # Add the new task to the database session and commit
            #db.session.commit()
            # add the new law query to the database session and commit
            # db.session.add(new_law_query) # Add the new task to the database session and commit
            #db.session.commit()
            #return redirect('/') # Redirect to the home page after adding the task
            return redirect('/response')
        except:
            return 'There was an issue adding your task' # Return an error message if there's an issue adding the task

    else: # If the method is GET, display current tasks
        #tasks = Todo.query.order_by(Todo.date_created).all() # Query the database for all tasks, ordered by creation date
        tasks = Todo.query.all()
        #outputs = Output.query.all()
        return render_template('index.html', tasks=tasks, keywords=keywords_for_mult_select, states=locations_for_mult_select) # Render the index template with the list of tasks


@app.route('/response')
def response():
    content = session.get('content', 'No content')
    location = session.get('location', [])
    options = session.get('options', [])
    return render_template('response.html', content=content, location=location, options=options)


# @app.route('/delete/<int:id>') # Define the delete route for a task, identified by its id
# def delete(id):
#     task_to_delete = Todo.query.get_or_404(id) # Retrieve the task by id or return 404 if not found

#     try:
#         db.session.delete(task_to_delete) # Delete the task from the database and commit the change
#         db.session.commit()
#         return redirect('/') # Redirect to the home page after deletion
#     except:
#         return 'There was a problem deleting that task' # Return an error message if there's a problem deleting the task

# @app.route('/update/<int:id>', methods=['GET', 'POST']) # Define the update route for a task, supporting both GET and POST methods
# def update(id):
#     task = Todo.query.get_or_404(id) # Retrieve the task by id or return 404 if not found

#     if request.method == 'POST': # If the method is POST, update the task
#         from sqlalchemy import and_

#         # Get the selected options and locations from the form
#         selected_options = request.form.getlist('options')
#         location_selected = request.form.getlist('location')

#         # Filter the database based on selected options and locations
#         # Assuming Law.location is the column for location in the Law model
#         laws = Law.query.with_entities(Law.law_text).filter(
#             and_(
#                 Law.keywords.like(f'%{selected_options}%'),
#                 Law.location.in_(location_selected)
#             )
#         ).all()

#         law_titles = Law.query.with_entities(Law.law_title).filter(
#             and_(
#                 Law.keywords.like(f'%{selected_options}%'),
#                 Law.location.in_(location_selected)
#             )
#         ).all()

#         task.content = request.form['content'] # Update the task content with the form data
#         # update the summary of the task content
#         summarizer = pipeline("summarization")
#         content_summary_from_model = summarizer(task.content, min_length=100, max_length=300,
#            clean_up_tokenization_spaces=True)[0]['summary_text']
#         task.content_summary = content_summary_from_model
#         try:
#             db.session.commit() # Commit the updates to the database
#             return redirect('/') # Redirect to the home page after updating the task
#         except:
#             return 'There was an issue updating your task' # Return an error message if there's an issue updating the task

#     else:
#         return render_template('update.html', task=task, content_summary=content_summary_from_model, laws=laws, law_titles=law_titles) # If the method is GET, render the update template with the task data


if __name__ == "__main__": # Conditional to ensure the script runs only if it is the main program
    # delete the database
    db.drop_all()
    # create the database
    db.create_all()
    load_data_from_csv('../data/clean_data.csv')
    app.run(debug=True) # Run the Flask application with debug mode enabled
