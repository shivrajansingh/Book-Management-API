# Book Management API

This is a Flask-based API for managing books, reviews, and generating summaries. The API provides endpoints for user authentication, CRUD operations on books, managing reviews, and generating book summaries using a summarization model.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [Authentication](#authentication)
  - [Books](#books)
  - [Reviews](#reviews)
  - [Recommendations](#recommendations)
  - [Summaries](#summaries)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the repository:**

    ```
    git clone https://github.com/shivrajansingh/book-management-api.git
    cd book-management-api
    ```

2. **Create a virtual environment and install dependencies:**

    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Set up the database:**

    ```
    flask db init
    flask db migrate
    flask db upgrade
    ```

4. **Run the application:**

    ```
    flask run
    ```

### Docker

1. **Build the Docker image:**

    ```
    docker build -t book-management-api .
    ```

2. **Run the Docker container:**

    ```
    docker run -p 5000:5000 book-management-api
    ```

## Usage

To use the API, you need to authenticate by logging in with the provided credentials. The API uses JWT for authentication.

### Authentication

- **Login:**

    ```
    POST /login
    ```

    **Request Body:**

   ```
    {
        "username": "admin",
        "password": "password"
    }
    ```

    **Response:**

   ```
    {
        "access_token": "your_access_token"
    }
    ```

### Books

- **Create a Book:**

    ```
    POST /books
    ```

    **Request Body:**

   ```
    {
        "title": "Book Title",
        "author": "Author Name",
        "description": "Book Description"
    }
    ```

    **Response:**

   ```
    {
        "id": 1
    }
    ```

- **Get All Books:**

    ```
    GET /books
    ```

    **Response:**

   ```
    [
        {
            "id": 1,
            "title": "Book Title",
            "author": "Author Name",
            "description": "Book Description"
        },
        ...
    ]
    ```

- **Get a Book by ID:**

    ```
    GET /books/<int:id>
    ```

    **Response:**

   ```
    {
        "id": 1,
        "title": "Book Title",
        "author": "Author Name",
        "description": "Book Description"
    }
    ```

- **Update a Book:**

    ```
    PUT /books/<int:id>
    ```

    **Request Body:**

   ```
    {
        "title": "Updated Title",
        "author": "Updated Author",
        "description": "Updated Description"
    }
    ```

    **Response:**

   ```
    {
        "id": 1,
        "title": "Updated Title",
        "author": "Updated Author",
        "description": "Updated Description"
    }
    ```

- **Delete a Book:**

    ```
    DELETE /books/<int:id>
    ```

    **Response:**

    ```
    Status Code: 204 No Content
    ```

### Reviews

- **Create a Review:**

    ```
    POST /books/<int:id>/reviews
    ```

    **Request Body:**

   ```
    {
        "rating": 5,
        "comment": "Great book!"
    }
    ```

    **Response:**

   ```
    {
        "id": 1
    }
    ```

- **Get All Reviews for a Book:**

    ```
    GET /books/<int:id>/reviews
    ```

    **Response:**

   ```
    [
        {
            "id": 1,
            "rating": 5,
            "comment": "Great book!"
        },
        ...
    ]
    ```

### Recommendations

- **Get Book Recommendations:**

    ```
    GET /recommendations
    ```

    **Query Parameters:**

    - `min_rating` (optional, default: 4.0): The minimum average rating for a book to be recommended.

    **Response:**

   ```
    [
        {
            "id": 1,
            "title": "Book Title",
            "author": "Author Name",
            "description": "Book Description"
        },
        ...
    ]
    ```

### Summaries

- **Generate a Summary:**

    ```
    POST /generate-summary
    ```

    **Request Body:**

   ```
    {
        "book_id": 1,
        "content": "Book content to be summarized"
    }
    ```

    **Response:**

   ```
    {
        "book_id": 1,
        "summary": "Generated summary text"
    }
    ```

- **Get a Summary by Book ID:**

    ```
    GET /books/<int:id>/summary
    ```

    **Response:**

   ```
    {
        "book_id": 1,
        "title": "Book Title",
        "author": "Author Name",
        "summary": "Generated summary text",
        "content": "Book content"
    }
    ```


## Documentation

The API documentation is available at `/swagger/` endpoint. You can access it by navigating to `http://localhost:5000/swagger/` in your web browser.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
