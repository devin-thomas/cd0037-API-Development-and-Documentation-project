import os
import unittest

from flaskr import create_app
from models import Category, Question, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_path = os.path.join(os.path.dirname(__file__), 'test_trivia.db')
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.database_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.seed_data()

    def tearDown(self):
        """Executed after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        if os.path.exists(self.database_path):
            os.remove(self.database_path)

    def seed_data(self):
        categories = [
            Category('Science'),
            Category('Art'),
            Category('Geography'),
            Category('History'),
        ]

        questions = [
            Question('What is the chemical symbol for gold?', 'Au', 1, 1),
            Question('What galaxy contains Earth?', 'The Milky Way', 1, 1),
            Question('Who painted The Starry Night?', 'Vincent van Gogh', 2, 2),
            Question('Which artist painted Guernica?', 'Pablo Picasso', 2, 2),
            Question('What is the capital of Kenya?', 'Nairobi', 3, 3),
            Question('What river runs through Egypt?', 'The Nile', 3, 3),
            Question('Who wrote the title character in Hamlet?', 'William Shakespeare', 4, 4),
            Question('In what year did Apollo 11 land on the moon?', '1969', 1, 4),
            Question('What planet is known as the Red Planet?', 'Mars', 1, 1),
            Question('Which ocean is the largest?', 'Pacific Ocean', 3, 3),
            Question('What style is Claude Monet associated with?', 'Impressionism', 2, 2),
            Question('Who was the first president of the United States?', 'George Washington', 4, 4),
        ]

        db.session.add_all(categories)
        db.session.add_all(questions)
        db.session.commit()

        self.existing_question_id = questions[0].id
        self.history_category_id = categories[-1].id

    def test_get_categories(self):
        response = self.client.get('/categories')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('1', data['categories'])
        self.assertEqual(data['categories']['1'], 'Science')

    def test_get_categories_not_found_when_empty(self):
        with self.app.app_context():
            Question.query.delete()
            Category.query.delete()
            db.session.commit()

        response = self.client.get('/categories')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_paginated_questions(self):
        response = self.client.get('/questions?page=1')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], 12)
        self.assertIn('categories', data)

    def test_get_paginated_questions_out_of_range(self):
        response = self.client.get('/questions?page=99')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        response = self.client.delete(f'/questions/{self.existing_question_id}')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], self.existing_question_id)

        with self.app.app_context():
            deleted_question = db.session.get(Question, self.existing_question_id)
            self.assertIsNone(deleted_question)

    def test_delete_missing_question(self):
        response = self.client.delete('/questions/9999')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        response = self.client.post('/questions', json={
            'question': 'What is 2 + 2?',
            'answer': '4',
            'category': 1,
            'difficulty': 1
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['created'], int)

        with self.app.app_context():
            created_question = db.session.get(Question, data['created'])
            self.assertIsNotNone(created_question)
            self.assertEqual(created_question.question, 'What is 2 + 2?')

    def test_create_question_bad_request(self):
        response = self.client.post('/questions', json={
            'question': 'Incomplete question'
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_search_questions(self):
        response = self.client.post('/questions', json={
            'searchTerm': 'title'
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total_questions'], 1)
        self.assertTrue(all('title' in question['question'].lower() for question in data['questions']))

    def test_get_questions_by_category(self):
        response = self.client.get(f'/categories/{self.history_category_id}/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'], 'History')
        self.assertGreater(len(data['questions']), 0)
        self.assertTrue(all(question['category'] == self.history_category_id for question in data['questions']))

    def test_get_questions_by_missing_category(self):
        response = self.client.get('/categories/9999/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_play_quiz(self):
        response = self.client.post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question'])
        self.assertEqual(data['question']['category'], 1)

    def test_play_quiz_bad_request(self):
        response = self.client.post('/quizzes', json={
            'quiz_category': {'type': 'Science', 'id': 1}
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')


if __name__ == '__main__':
    unittest.main()
