import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from utils import create_mock_question
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_for_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        #now checks for all responses
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']),6)
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data) 

        #now checks for all responses 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
    
    def test_error_for_not_found_page(self):
        response = self.client().get('/questions?page=10000000')
        data = json.loads(response.data)

        # now checks
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_successful_for_question_delete(self):
        mock_question_id = create_mock_question()
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        #now checks
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")
    def test_for_delete_question_id_not_exist(self):
        response = self.client().delete('/questions/123456789')
        data = json.loads(response.data)

        # now check
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')
    def test_for_create_questions(self):
        mock_data = {
            'question': 'This is a mock question',
            'answer': 'this is a mock answer',
            'difficulty': 1,
            'category': 1,
        }
        response = self.client().post('/questions', json=mock_data)
        data = json.loads(response.data)

        # check
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_search_questions(self):
        request_data = {
            'searchTerm': 'Harry porter',
        }
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_search_term_not_found(self):
        request_data = {
            'searchTerm': 'kngkbsjbhfihihgfiuhwihr74yg',
        }

        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

    
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

if __name__ == "__main__":
    unittest.main()