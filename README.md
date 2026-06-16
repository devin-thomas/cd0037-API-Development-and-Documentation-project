# Trivia API

Udacity's trivia project is a full-stack app with a Flask API backend and a React frontend. The backend supports listing questions, filtering by category, searching, creating and deleting questions, and serving randomized quiz questions.

## Project Structure

- `backend/`: Flask API, SQLAlchemy models, database seed file, and tests
- `frontend/`: React client that consumes the API

## Setup

### Backend

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Configure database environment variables.

Required for local Postgres use:

```bash
set DB_NAME=trivia
set DB_USER=postgres
set DB_PASSWORD=password
set DB_HOST=localhost:5432
```

Optional shortcut:

```bash
set DATABASE_URL=postgresql://postgres:password@localhost:5432/trivia
```

4. Create and seed the database:

```bash
createdb trivia
psql trivia < trivia.psql
```

5. Start the API server:

```bash
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run
```

The API runs at `http://127.0.0.1:5000`.

### Frontend

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start the React development server:

```bash
npm start
```

The frontend runs at `http://localhost:3000`.

## Running Tests

The included test suite uses a self-seeded SQLite database, so it can run without creating a separate Postgres test database.

```bash
cd backend
python test_flaskr.py
```

## API Overview

Base URL: `http://127.0.0.1:5000`

All responses are JSON and include a `success` flag.

### `GET /categories`

- Fetches all available categories.
- Request Arguments: None
- Returns:

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### `GET /questions?page={page_number}`

- Fetches a paginated list of questions.
- Request Arguments:
  - `page` integer query parameter, defaults to `1`
- Returns:

```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2
    }
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

### `GET /categories/{category_id}/questions`

- Fetches all questions for a specific category.
- Request Arguments:
  - `category_id` path parameter
- Returns:

```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2
    }
  ],
  "total_questions": 4,
  "current_category": "History"
}
```

### `POST /questions`

- Creates a new question when the request body includes `question`, `answer`, `category`, and `difficulty`.
- Request Body:

```json
{
  "question": "What is 2 + 2?",
  "answer": "4",
  "category": 1,
  "difficulty": 1
}
```

- Returns:

```json
{
  "success": true,
  "created": 24
}
```

### `POST /questions` for search

- Searches questions when the request body includes `searchTerm`.
- Request Body:

```json
{
  "searchTerm": "title"
}
```

- Returns:

```json
{
  "success": true,
  "questions": [
    {
      "id": 7,
      "question": "Who wrote the title character in Hamlet?",
      "answer": "William Shakespeare",
      "category": 4,
      "difficulty": 4
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

### `DELETE /questions/{question_id}`

- Deletes a question by id.
- Request Arguments:
  - `question_id` path parameter
- Returns:

```json
{
  "success": true,
  "deleted": 24
}
```

### `POST /quizzes`

- Returns the next random question for quiz play, excluding previously asked questions. When `quiz_category.id` is `0`, the API uses all categories.
- Request Body:

```json
{
  "previous_questions": [5, 9],
  "quiz_category": {
    "type": "History",
    "id": 4
  }
}
```

- Returns:

```json
{
  "success": true,
  "question": {
    "id": 12,
    "question": "Who invented Peanut Butter?",
    "answer": "George Washington Carver",
    "category": 4,
    "difficulty": 2
  }
}
```

If no unasked questions remain, `question` is `null`.

## Error Responses

Example error response:

```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

Common error codes returned by the API:

- `400` bad request
- `404` resource not found
- `405` method not allowed
- `422` unprocessable
- `500` internal server error
