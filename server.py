import os
from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route('/')
def mainIndex():
    header_img = random.randint(1,5);
    return render_template("index.html", header_num = header_img);
    
@app.route('/article_test')
def article():
    return render_template("article.html");

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)