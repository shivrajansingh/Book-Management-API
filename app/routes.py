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
        """
        Login endpoint.
        Handles user login by accepting a POST request with a JSON payload containing 
        the username and password. If the credentials are valid, returns a JSON response 
        with an access token and a 200 status code. Otherwise, returns a JSON response 
        with an error message and a 401 status code.
        use username : admin and password : password for testing
        """
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
        """
        Get All Books.
        Get all books from the database and return them as a JSON response.

        Returns:
            A JSON response containing a list of dictionaries, where each dictionary
            represents a book and contains the following keys: 'id', 'title', 'author',
            and 'description'.

        Raises:
            None.
        """
        books = Book.query.all()
        return books

    @api.expect(book_model, validate=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self):
        """
        Create a book
        Handles the creation of a new book by accepting a POST request with a JSON payload 
        containing the book's title, author, and optional description. The function then 
        creates a new Book object, adds it to the database session, and commits the changes. 
        It returns a JSON response with the ID of the newly created book and a 201 status code.
        """
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
        """
        Get a Book.
        Retrieves a book by its ID and returns its details as a JSON response.

        Parameters:
            id (int): The ID of the book to retrieve.

        Returns:
            A JSON response containing the book's ID, title, author, and description.
        """
        book = Book.query.get_or_404(id)
        return book

    @api.expect(book_model, validate=True)
    @api.marshal_with(book_model)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def put(self, id):
        """
        update a book.
        Updates a book by its ID and returns its updated details as a JSON response.

        Parameters:
            id (int): The ID of the book to update.

        Returns:
            A JSON response containing the book's ID, title, author, and description.
        """
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
        """
        Delete a book.
        Deletes a book by its ID and returns a success response.

        Parameters:
            id (int): The ID of the book to delete.

        Returns:
            An empty response with a 204 status code.
        """
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
        """
        Get All Reviews of a Book.
        Retrieves all reviews for a book with the given ID.

        Parameters:
            id (int): The ID of the book to retrieve reviews for.

        Returns:
            A JSON response containing a list of dictionaries, where each dictionary represents a review and contains the following keys: 'id', 'rating', and 'comment'.
        """
        book = Book.query.get_or_404(id)
        reviews = Review.query.filter_by(book_id=book.id).all()
        return reviews

    @api.expect(review_model, validate=True)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self, id):
        """
        Create a Review for a Book.
        Creates a review for a book with the given ID and returns the ID of the created review as a JSON response.

        Parameters:
            id (int): The ID of the book to create a review for.

        Returns:
            A JSON response containing the ID of the created review.
            The response has a status code of 201 (Created).
        """
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
        """
        Get Recommendations.
        Retrieves book recommendations based on a minimum average rating.
        Parameters:
            min_rating (float): The minimum average rating for a book to be recommended (default is 4.0).
        Returns:
            A JSON response containing a list of dictionaries, where each dictionary represents a recommended book and contains the following keys: 'id', 'title', 'author', and 'description'.
        """
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
        """
        Generate Summary for a book content. 
        Generates a summary for a given book content using the LLAMA3.1 Model, it uses the content to generate the summary

        Parameters:
            book_id (int): The ID of the book.
            content (str): The content of the book.

        Returns:
            A JSON response containing the book ID and the generated summary.
            The response has a status code of 201 (Created) if successful.
            If the book ID or content is missing, returns a JSON error response with a 400 status code.
            If the book is not found, returns a JSON error response with a 404 status code.
        """
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
        """
        Get Summary for a book.
        Retrieves the summary of a book with the given ID.

        Parameters:
            id (int): The ID of the book.

        Returns:
            A JSON response containing the book ID, title, author, summary, and content.
            The response has a status code of 200 if successful.
            If no summary is found for the book, returns a JSON error response with a 404 status code.
        """
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
