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
