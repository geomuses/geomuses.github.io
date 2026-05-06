from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    favorite_foods = ["Pizza", "Burger", "Ice Cream"]
    return render_template('index.html', name="John", age=30, favorite_foods=favorite_foods)

if __name__ == '__main__':
    app.run(debug=True)