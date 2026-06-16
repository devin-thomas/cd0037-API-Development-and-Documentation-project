import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from models import Category, Question, db, setup_db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return [question.format() for question in questions[start:end]]


def format_categories():
    categories = Category.query.order_by(Category.id).all()
    return {str(category.id): category.type for category in categories}


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        app.config.update(test_config)
        setup_db(app, database_path=test_config.get('SQLALCHEMY_DATABASE_URI'))

    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
        return response

    @app.get('/categories')
    def get_categories():
        categories = format_categories()
        if not categories:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories
        })

    @app.get('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if not current_questions and selection:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': format_categories(),
            'current_category': None
        })

    @app.delete('/questions/<int:question_id>')
    def delete_question(question_id):
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True,
            'deleted': question_id
        })

    @app.post('/questions')
    def create_or_search_questions():
        body = request.get_json(silent=True)
        if body is None:
            abort(400)

        search_term = body.get('searchTerm')
        if search_term is not None:
            results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).order_by(Question.id).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in results],
                'total_questions': len(results),
                'current_category': None
            })

        question_text = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')

        if not all([question_text, answer, category, difficulty]):
            abort(400)

        try:
            question = Question(
                question=question_text,
                answer=answer,
                category=int(category),
                difficulty=int(difficulty)
            )
            question.insert()
            created_question_id = question.id
        except Exception:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'created': created_question_id
        }), 201

    @app.get('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = db.session.get(Category, category_id)
        if category is None:
            abort(404)

        questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category.type
        })

    @app.post('/quizzes')
    def play_quiz():
        body = request.get_json(silent=True)
        if body is None:
            abort(400)

        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        if previous_questions is None or quiz_category is None:
            abort(400)

        selected_category_id = int(quiz_category.get('id', 0) or 0)

        if selected_category_id == 0:
            candidate_questions = Question.query.order_by(Question.id).all()
        else:
            category = db.session.get(Category, selected_category_id)
            if category is None:
                abort(404)
            candidate_questions = Question.query.filter(
                Question.category == selected_category_id
            ).order_by(Question.id).all()

        available_questions = [
            question for question in candidate_questions
            if question.id not in previous_questions
        ]

        return jsonify({
            'success': True,
            'question': random.choice(available_questions).format() if available_questions else None
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
