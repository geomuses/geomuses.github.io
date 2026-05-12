from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 自動遞增 ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # 使用者名稱
    password = db.Column(db.String(120), nullable=False)  # 密碼
    email = db.Column(db.String(120), unique=True, nullable=True)  # 電子信箱

    def __repr__(self):
        return f'<User {self.username}>'