from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "I\'m geo"

@app.route("/user/<username>")
def show_user(username):
    return f"Hello, {username}!"

@app.route("/square/<number>")
def square(number):
    return f'{number**2}'

if __name__ == "__main__":
    
    app.run(debug=True)