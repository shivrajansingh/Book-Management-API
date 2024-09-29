from flask import Blueprint, request, jsonify, abort
from .models import db, Book, Review, Summary
from .util import summarize
from flask_jwt_extended import jwt_required, create_access_token
from flask_restx import Api, Resource, fields, Namespace

bp = Blueprint('main', __name__)
api = Api(bp, doc='/swagger/', title='Book Management API', version='1.0', description='API for managing books, reviews, and generating summaries')

ns = Namespace('api', description='Book operations')
api.add_namespace(ns)

login_model = api.model('Login', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The password')
})

book_model = api.model('Book', {
    'id': fields.Integer(readonly=True, description='The book unique identifier'),
    'title': fields.String(required=True, description='The book title'),
    'author': fields.String(required=True, description='The book author'),
    'description': fields.String(description='The book description')
})

review_model = api.model('Review', {
    'id': fields.Integer(readonly=True, description='The review unique identifier'),
    'rating': fields.Integer(required=True, description='The review rating'),
    'comment': fields.String(description='The review comment')
})

summary_model = api.model('Summary', {
    'book_id': fields.Integer(required=True, description='The book unique identifier'),
    'content': fields.String(required=True, description='The book content'),
    'summary': fields.String(description='The generated summary')
})

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api.authorizations = authorizations


### 1. Login Resource ###
@ns.route('/login', methods=['POST'])
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if username == 'admin' and password == 'password':
            access_token = create_access_token(identity={'username': username})
            return {'access_token': access_token}, 200

        return {'msg': 'Bad username or password'}, 401


### 2. Books Resource ###
@ns.route('/books', methods=['GET', 'POST'])
class Books(Resource):
    @api.marshal_with(book_model, as_list=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self):
        books = Book.query.all()
        return books

    @api.expect(book_model, validate=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self):
        data = request.get_json()
        new_book = Book(title=data['title'], author=data['author'], description=data.get('description'))
        db.session.add(new_book)
        db.session.commit()
        return {'id': new_book.id}, 201

@ns.route('/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
class BookDetail(Resource):
    @api.marshal_with(book_model)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self, id):
        book = Book.query.get_or_404(id)
        return book

    @api.expect(book_model, validate=True)
    @api.marshal_with(book_model)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def put(self, id):
        book = Book.query.get_or_404(id)
        data = request.get_json()
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'description' in data:
            book.description = data['description']
        db.session.commit()
        return book

    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, id):
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return '', 204


### 3. Reviews Resource ###
@ns.route('/books/<int:id>/reviews', methods=['GET', 'POST'])
class Reviews(Resource):
    @api.marshal_with(review_model, as_list=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self, id):
        book = Book.query.get_or_404(id)
        reviews = Review.query.filter_by(book_id=book.id).all()
        return reviews

    @api.expect(review_model, validate=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self, id):
        book = Book.query.get_or_404(id)
        data = request.get_json()
        new_review = Review(book_id=book.id, rating=data['rating'], comment=data.get('comment'))
        db.session.add(new_review)
        db.session.commit()
        return {'id': new_review.id}, 201


### 4. Recommendations Resource ###
@ns.route('/recommendations', methods=['GET'])
class Recommendations(Resource):
    @api.marshal_with(book_model, as_list=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self):
        min_rating = float(request.args.get('min_rating', 4.0))
        books = Book.query.all()
        recommendations = []
        for book in books:
            reviews = Review.query.filter_by(book_id=book.id).all()
            if reviews:
                average_rating = sum([review.rating for review in reviews]) / len(reviews)
                if average_rating >= min_rating:
                    recommendations.append(book)
        return recommendations


### 5. Summary Resource ###
@ns.route('/generate-summary', methods=['POST'])
class GenerateSummary(Resource):
    @api.expect(summary_model, validate=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self):
        data = request.get_json()

        book_id = data.get('book_id')
        content = data.get('content')

        if not book_id or not content:
            return {'error': 'book_id and content are required'}, 400

        book = Book.query.get(book_id)
        if not book:
            return {'error': 'Book not found'}, 404

        try:
            summary_text = summarize(content)
        except ValueError as e:
            return {'error': str(e)}, 400

        if summary_text == False:
            return {'error': "Summary is not generated by the LLAMA3.1 Model"}, 400

        summary = Summary(book_id=book_id, content=content, summary=summary_text)
        db.session.add(summary)
        db.session.commit()

        return {
            'book_id': summary.book_id,
            'summary': summary.summary
        }, 201

@ns.route('/books/<int:id>/summary', methods=['GET'])
class GetSummary(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self, id):
        book = Book.query.get_or_404(id)
        summary = Summary.query.filter_by(book_id=book.id).first()

        if not summary:
            abort(404, description="No summary found for this book")

        return jsonify({
            'book_id': book.id,
            'title': book.title,
            'author': book.author,
            'summary': summary.summary,
            'content': summary.content
        })
