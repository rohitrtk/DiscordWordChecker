from flask import Flask
from threading import Thread

app = Flask('')

host = '0.0.0.0'
port = 8080

@app.route('/')
def home():
    return 'Discord Word Checker bot is running.'

def run():
    app.run(host=host, port=port)

def keep_running():
    thread = Thread(target=run)
    thread.start()
