#import packages
from flask import Flask, render_template, request, jsonify
import openai
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

#initiate Flask application
app = Flask(__name__)
#add API Key
openai.api_key  = "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"

#set up pretrained summarization model using Pegasus
model_name = "google/pegasus-xsum" #model created by Google
tokenizer = PegasusTokenizer.from_pretrained(model_name) #initiate tokenizer
device = "cuda" if torch.cuda.is_available() else "cpu" #use GPU where available
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device) #load the model

def get_completion(prompt, model="gpt-3.5-turbo"):
    # function to get repoinses in the chat
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # creating deterministic model
    )
    return response.choices[0].message["content"]

def summarize(input_text):
    # function to summarizes text input from the chat
    input_text = "summarize: " + input_text # show the model what needs to be summarized
    # tokenize inputs and enable truncation
    tokenized_text = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True).to(device)
    # generate summary (min and max can be adjusted)
    summary_ = model.generate(tokenized_text, min_length=30, max_length=300)
    # decode summary into a string
    summary = tokenizer.decode(summary_[0], skip_special_tokens=True)
    return summary

@app.route("/")
def home():  
    # define path to home page
    return render_template("index.html")

@app.route("/get")
def get_bot_response():   
    # define path to model
    userText = request.args.get('msg') # get input
    response = get_completion(userText) # get response  
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

# run the script above
if __name__ == "__main__":
    app.run()