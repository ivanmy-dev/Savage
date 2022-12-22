from savage import db

class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.Text)

    def __init__(self, username, email, password) -> None:
        self.username = username
        self.email = email
        self.password = password
    
    def __repr__(self) -> str:
        return f'User: {self.username}'


class Img(db.Model):
    __tablename__ = 'img'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    img = db.Column(db.LargeBinary)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

    def __init__(self, img, name, mimetype) -> None:
        self.img = img
        self.name = name
        self.mimetype = mimetype
