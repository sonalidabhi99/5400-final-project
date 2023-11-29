from flask import Flask, render_template, request, jsonify
import openai
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

app = Flask(__name__)
openai.api_key  = "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"

model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def summarize(input_text):
    input_text = "summarize: " + input_text
    tokenized_text = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True).to(device)
    summary_ = model.generate(tokenized_text, min_length=30, max_length=300)
    summary = tokenizer.decode(summary_[0], skip_special_tokens=True)
    return summary

@app.route("/")
def home():    
    return render_template("index.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    response = get_completion(userText)  
    #return str(bot.get_response(userText)) 
    return response

@app.route("/summarize", methods=["POST"])
def get_summary():
    try:
        input_text = request.form.get('text', '')  # Safely get the text field
        summary = summarize(input_text)
        return jsonify({"summary": summary})
    except Exception as e:
        print(e)  # Log the exception for debugging
        return jsonify({"error": "An error occurred during summarization."}), 500


if __name__ == "__main__":
    app.run()