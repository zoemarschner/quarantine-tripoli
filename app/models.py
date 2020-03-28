from app import db

class Setting(db.Model):
    name = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Integer)

    def __repr__(self):
        return '<Setting {}>'.format(self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    ready = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.name)