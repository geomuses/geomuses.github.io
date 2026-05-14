---
layout: post
title: python flask 数据库 CRUD
date: 2026-05-13 11:24:29 +0800
tags:
  - python
  - flask
image: 07.jpg
---
* **密碼安全性**：目前的範例是存明文（Plain Text），實務上請使用 `werkzeug.security` 的 `generate_password_hash` 進行加密。
* **路徑檢查**：確保你的專案目錄結構如下：
```text
/app
├── app.py
├── models.py
├── templates/
│   └── index.html
└── instance/ (自動生成，存放 data.db)
```

models.py`

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

```

`app.py`

實作了完整的 CRUD 路由邏輯

```python
from flask import Flask, render_template, request, redirect, url_for
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 初始化資料庫與種子資料
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="geo").first():
        db.session.add(User(username="geo", password="ge0"))
        db.session.commit()

# --- CRUD 路由 ---

# 1. Read (讀取全部)
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# 2. Create (新增)
@app.route('/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('index'))

# 3. Update (更新資料 - 範例為修改用戶名)
@app.route('/update/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get_or_404(id)
    user.username = request.form.get('username')
    db.session.commit()
    return redirect(url_for('index'))

# 4. Delete (刪除)
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

```

 `templates/index.html`

提供一個簡單的介面來操作這些功能：

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>Flask CRUD 範例</title>
</head>
<body>
    <h1>用戶管理系統</h1>

    <!-- 新增用戶表單 -->
    <form action="/add" method="POST">
        <input type="text" name="username" placeholder="用戶名" required>
        <input type="password" name="password" placeholder="密碼" required>
        <button type="submit">新增用戶</button>
    </form>

    <hr>

    <!-- 用戶列表與刪除/更新功能 -->
    <table border="1">
        <tr>
            <th>ID</th>
            <th>用戶名</th>
            <th>操作</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>
                <form action="/update/{{ user.id }}" method="POST" style="display:inline;">
                    <input type="text" name="username" value="{{ user.username }}">
                    <button type="submit">修改名稱</button>
                </form>
            </td>
            <td>
                <a href="/delete/{{ user.id }}" onclick="return confirm('確定刪除嗎？')">刪除</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>

```

