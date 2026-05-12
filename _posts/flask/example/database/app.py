from flask import Flask , render_template
# from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
app = Flask(__name__)

# 資料庫設定：使用 SQLite（可換成 PostgreSQL, MySQL）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 不要跟踪对象的修改并发送信号

# 稍後我們會導入 models
from models import User

@app.route('/')
def index():
    users = User.query.all()  # 查询全部用户
    return render_template('index.html', users=users)
    
if __name__ == '__main__':

    from models import db

    # 初始化資料庫
    db.init_app(app)

    with app.app_context():
        db.create_all()  # 建立所有模型對應的資料表 

        existing_user = User.query.filter_by(username="geo").first() 
        if not existing_user: 
            user = User( username="geo", password="ge0" ) 
            db.session.add(user)    
            db.session.commit() 
            print("新用户 geo 已创建！") 
        else: print("用户 geo 已存在，跳过创建步骤。")

    app.run(debug=True)