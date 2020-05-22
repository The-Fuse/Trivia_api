import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from utils import create_mock_question


class TriviaTestCase(unittest.TestCase):
    
    def setUp(self):

        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', 'postgres', 'localhost:5432', self.database_name)

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

    def test_get_all_categories(self):
        """Test for get_all_categories

        Tests for the status code, if success is true,
        if categories is returned and the length of
        the returned categories
        """

        # make request and process response
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_paginated_questions(self):
        """Test for get all paginated questions

        This tests the return values for a successful
        return of paginated questions

        the assertion that ensures the paginated questions
        is always 10, is determined by a constant that could
        change.
        """
        # make request and process response
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_error_for_out_of_bound_page(self):
        """Test for out of bound page

        This test ensures a page that is out of bound
        returns a 404 error
        """

        # make request and process response
        response = self.client().get('/questions?page=10000000')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_successful_question_delete(self):
        
        mock_question_id = create_mock_question()

        # delete mock question and process response
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        # ensure question does not exist
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")

    def test_delete_same_question_twice(self):
        

        mock_question_id = create_mock_question()

        # this tests if resource has already been deleted
        self.client().delete('/questions/{}'.format(mock_question_id))
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_id_not_exist(self):
       
        # this tests an id that doesn't exist
        response = self.client().delete('/questions/1211256')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_with_invalid_id(self):
     
        response = self.client().delete('/questions/sadsa2112kjsds6')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_questions(self):
       
        # mock data to use as payload for post request
        mock_data = {
            'question': 'This is a mock question',
            'answer': 'this is a mock answer',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=mock_data)
        data = json.loads(response.data)

        # asserions to ensure successful request
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_create_question_with_empty_data(self):
        """Test for ensuring data with empty fields are not processed."""
        request_data = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_questions(self):
       

        request_data = {
            'searchTerm': 'largest lake in Africa',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_empty_search_term_response(self):
        """Test for empty search term."""

        request_data = {
            'searchTerm': '',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_term_not_found(self):
      

        request_data = {
            'searchTerm': 'dfjdtrertwfresyg346474yg',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_questions_by_category(self):
        """Test for getting questions by category."""

        # make a request for the Sports category with id of 6
        response = self.client().get('/categories/6/questions')
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Sports')

  
    def test_play_quiz_questions(self):
        """Tests playing quiz questions"""

        # mock request data
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

   
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

    
        self.assertEqual(data['question']['category'], 4)

 


if __name__ == "__main__":
    unittest.main()
