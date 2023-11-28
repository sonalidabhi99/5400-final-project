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
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__) # Initialize a Flask application
app.secret_key = 'super_secret_key' # Set a secret key for the application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # Configure the application to use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # Initialize SQLAlchemy with the Flask app
migrate = Migrate(app, db) # WHEN WE CHANGE THE DATABASE--UNCOMMENT THIS LINE ON THE FIRST RUN; Initialize Flask-Migrate with the Flask app and SQLAlchemy database

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    location = db.Column(db.String(500))
    options = db.Column(db.String(500))
    law_titles = db.Column(db.Text)  # Assuming this could be a long text
    law_texts = db.Column(db.Text)   # Same here
    laws_summary = db.Column(db.Text)

# class Todo(db.Model): # Define a Todo model for the SQLAlchemy ORM
#     id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
#     content = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     #date_created = db.Column(db.DateTime, default=datetime.utcnow) # Define 'date_created' column with a default value of the current UTC time
#     content_summary = db.Column(db.String(200), default="hi")#nullable=False) # instead of date_created, we will do a summary of the content

#     def __repr__(self): # Representation method to display a task's ID
#         return '<Task %r>' % self.id

# class Law(db.Model): # Define a Todo model for the SQLAlchemy ORM
#     id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
#     law_title = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     law_text = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     location = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     type = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     keywords = db.Column(db.String(200), nullable=False) # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     def __repr__(self): # Representation method to display a task's ID
#         return '<Task %r>' % self.id

# class Output(db.Model): # Define a Todo model for the SQLAlchemy ORM
#     id = db.Column(db.Integer, primary_key=True) # Define the 'id' column as an integer and primary key
#     law_titles_included = db.Column(db.String(200), default="no laws found") # Define the 'content' column as a string with a maximum length of 200 characters, cannot be null
#     #date_created = db.Column(db.DateTime, default=datetime.utcnow) # Define 'date_created' column with a default value of the current UTC time
#     laws_summary = db.Column(db.String(200), default="no laws to summarize")#nullable=False) # instead of date_created, we will do a summary of the content

#     def __repr__(self): # Representation method to display a task's ID
#         return '<Task %r>' % self.id

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


    if request.method == 'POST': # If the method is POST, add a new task
        

        # Get the selected options and locations from the form
        selected_options = request.form.getlist('options')
        location_selected = request.form.getlist('location')
        task_content = request.form['content'] # Retrieve the task content from the form data

        # retrieve the summary of the task content
        # summarizer = pipeline("summarization") # load the model
        # content_summary_from_model = summarizer(task_content, min_length=10, max_length=25,
        #    clean_up_tokenization_spaces=True)[0]['summary_text']

        # session['content'] = task_content
        # session['location'] = location_selected
        # session['options'] = selected_options
        try:
            df = pd.read_csv('../data/clean_data.csv')
            # filter df for regex of selected options in keywords column--return list of laws
            try:
                laws = df[df['Keywords'].str.contains('|'.join(selected_options), case=False)]
            except:
                laws = df
            
            try:
                # filter df for regex of selected locations in location column--return list of laws
                laws = laws[laws['location'].str.contains('|'.join(location_selected), case=False)]
            except:
                laws = laws

            # get the law titles
            law_titles = laws['law_title'].tolist()
            # get the law texts
            law_texts = laws['law_text'].tolist()

            # # create a new output object
            # session['law_titles'] = law_titles
            # session['law_texts'] = law_texts
            # session['laws_summary'] = 'Will add summary here later'
            user_data = UserData(
                content=task_content,
                location=','.join(location_selected),  # Convert list to string
                options=','.join(selected_options),    # Same as above
                law_titles=','.join(law_titles),       # Assuming law_titles is a list
                law_texts=','.join(law_texts),         # Same here
                laws_summary='Will add summary here later'
            )
            db.session.add(user_data)
            db.session.commit()

            return redirect('/response')
        except Exception as e:
            print("Error:", e)
            return 'There was an issue adding your task' # Return an error message if there's an issue adding the task

    else: # If the method is GET, display current tasks
        return render_template('index.html', keywords=keywords_for_mult_select, states=locations_for_mult_select) # tasks=tasks, # Render the index template with the list of tasks


@app.route('/response')
def response():
    # content = session.get('content', 'No content')
    # location = session.get('location', [])
    # options = session.get('options', [])
    # law_titles = session.get('law_titles', [])
    # law_texts = session.get('law_texts', [])
    # laws_summary = session.get('laws_summary', 'No laws summary')
    # return render_template('response.html', content=content, location=location, options=options, law_titles=law_titles, law_texts=law_texts, laws_summary=laws_summary)
    user_data = UserData.query.order_by(UserData.id.desc()).first()  # Get the latest entry
    if user_data:
        content = user_data.content
        location = user_data.location.split(',')  # Convert string back to list
        options = user_data.options.split(',')    # Same as above
        law_titles = user_data.law_titles.split(',')
        law_texts = user_data.law_texts.split(',')
        laws_summary = user_data.laws_summary
    else:
        # Default values if no data is found
        content = 'No content'
        location = []
        options = []
        law_titles = []
        law_texts = []
        laws_summary = 'No laws summary'

    return render_template('response.html', content=content, location=location, options=options, law_titles=law_titles, law_texts=law_texts, laws_summary=laws_summary)



if __name__ == "__main__": # Conditional to ensure the script runs only if it is the main program
    db.create_all()
    app.run(debug=True) # Run the Flask application with debug mode enabled

    # delete the database
    #db.drop_all()
    # create the database
    #db.create_all()
    #load_data_from_csv('../data/clean_data.csv')