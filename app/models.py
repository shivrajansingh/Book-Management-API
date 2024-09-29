from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    reviews = db.relationship('Review', backref='book', lazy=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String)

class Summary(db.Model):
    __tablename__ = "summaries"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)

    book = db.relationship('Book', backref=db.backref('summary', uselist=False))