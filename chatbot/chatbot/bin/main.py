from flask import Flask, render_template, request, jsonify
from ..app import app
#MUST BE IN UPPER MOST CHATBOT FOLDER FOR EVERYTHING TO WORK (RELATIVE PATHS :( )
if __name__ == "__main__":
    app.run()