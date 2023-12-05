from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

def summarize_initialize():
    """
    a function to initialize the summarizer for the summarizer function
    params: none
    returns: the tokenizer and model
    """
    #set up pretrained summarization model using Pegasus
    model_name = "google/pegasus-xsum" 
    tokenizer = PegasusTokenizer.from_pretrained(model_name)  
    device = "cuda" if torch.cuda.is_available() else "cpu" 
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device) 
    return tokenizer, model, device 

def summarize(input_text):
    """
    the summarizer function; uses pegasus to summarize the user text
    params: input_text: string of the user input
    output: summary: text of the summary created by the summarizer
    """
    tokenizer, model, device = summarize_initialize()
    # function to summarizes text input from the chat
    input_text = "summarize: " + input_text # show the model what needs to be summarized
    # tokenize inputs and enable truncation
    tokenized_text = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True).to(device)
    # generate summary (min and max can be adjusted)
    summary_ = model.generate(tokenized_text, min_length=30, max_length=300)
    # decode summary into a string
    summary = tokenizer.decode(summary_[0], skip_special_tokens=True)
    return summary