from flask import Flask, render_template

app = Flask(__name__)

# 创建404错误处理函数
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def home():
    return "Welcome to the homepage!"

if __name__ == '__main__':
    app.run(debug=True)