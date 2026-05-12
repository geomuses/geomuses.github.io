from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 資料庫設定：使用 SQLite（可換成 PostgreSQL, MySQL）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db = SQLAlchemy(app)

# 稍後我們會導入 models
# from models import User

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':

    from models import User
    with app.app_context():
        db.create_all()  # 建立所有模型對應的資料表

    app.run(debug=True)