#import packages
from flask import Flask, render_template, request, jsonify
import logging
# hide warnings
import warnings
warnings.filterwarnings('ignore')

#calling functions from the functions folder: 
from chatbot.functions.information_retrieval import *
from chatbot.functions.summarizer import *

#initiate Flask application
app = Flask(__name__)

@app.route("/")
def home():  
    # define path to home page
    return render_template("index.html")

@app.route("/get")
def get_bot_response():   
    # define path to model
    userText = request.args.get('msg') # get input
    response = summarize(userText) # get response  
    #return str(bot.get_response(userText)) 
    return response


@app.route("/summarize", methods=["POST"])
def get_summary():
    # define path for text summarization
    try:
        input_text = request.form.get('text', '')  # get text from the input
        summary = summarize(input_text) # get summary of the text
        return jsonify({"summary": summary})
    except Exception as e:
        print(e)  # log the exception for debugging
        return jsonify({"error": "An error occurred during summarization."}), 500

@app.route("/process_input", methods=["POST"])
def process_input():
    logging.basicConfig(level=logging.INFO)
    logging.info('Initializing the app')
    try:
        location = request.form.get('input1', '')
        user_issue = request.form.get('input2', '')
        cleaned_text = clean_text(user_issue)
        logging.info('cleaned user text')
        idx = find_most_similar_law(location, cleaned_text)
        logging.info(f'law {idx} pulled')
        law_text, law_title = get_law(idx)
        summary = summarize(law_text)
        logging.info('summary created')
        return jsonify({"most_similar_law": law_title, "summary": summary})
    
    except Exception as e:
        print(e)  # log the exception for debugging
        return jsonify({"error": "An error occurred processing the inputs."}), 500
