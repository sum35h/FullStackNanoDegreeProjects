import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','password','localhost:5432', self.database_name)


        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.drop_all()
            # create all tables
            self.db.create_all()
            
    
    def tearDown(self):
        """Executed after each test"""
        print("teardown")
        with self.app.app_context():
            try:
                self.db.session.query(Category).delete()
                self.db.session.query(Question).delete()
                self.db.session.commit()
            except Exception as e:
                print('error',e)
                self.db.session.rollback()


    def prerequest_create_categories(self):
        with self.app.app_context():
            try:
                category_list=['Science','History','Entertainment','Sports']
                categories =  [Category(type=c) for c in category_list]
                Category.query.delete()

                self.db.session.add_all(categories)
                self.db.session.commit()
                return Category.query.filter(Category.type=='Sports').first()
            except Exception as e:
                print('error',e)
                self.db.session.rollback()

    def test_valid_fetch_categories(self):
        category = self.prerequest_create_categories()
        
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['categories']),4)

    def test_invalid_fetch_questions(self):
        self.prerequest_create_categories()
        response = self.client().get('/questions')
        
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(response.status_code,400)

    def test_valid_create_and_and_fetch_question(self):
        category = self.prerequest_create_categories()
        payload = {'question':'test ?','answer':'test','dificulty':'3','category':category.id}
        response = self.client().post('/questions',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['totalQuestions'],1)

    def test_valid_delete_question(self):
        category = self.prerequest_create_categories()
        payload = {'question':'test ?','answer':'test','dificulty':'3','category':category.id}
        response = self.client().post('/questions',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        
        response = self.client().delete('/questions/'+str(data['id']))
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

    def test_invalid_delete_question(self):
         
        response = self.client().delete('/questions/22')
        data = json.loads(response.data)
        self.assertEqual(response.status_code,400)
        self.assertEqual(data['success'],False)

    def test_valid_fetch_questions_by_category(self):
        category = self.prerequest_create_categories()
        payload = {'question':'test ?','answer':'test','dificulty':'3','category':category.id}
        response = self.client().post('/questions',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

        response = self.client().get('/categories/'+str(category.id)+'/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(len(data['questions']),1)
    
    def test_invalid_fetch_questions_by_category(self):
        

        response = self.client().get('/categories/123/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
       

def test_valid_search_questions(self):
        category = self.prerequest_create_categories()
        payload = {'question':'test ?','answer':'test','dificulty':'3','category':category.id}
        response = self.client().post('/questions',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

        payload = {'searchTerm':'test'}
        response = self.client().post('/questions/search',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['totalQuestions']),1)

def test_valid_quizzes(self):
        category = self.prerequest_create_categories()

        payload = {'question':'test ?','answer':'test','dificulty':'3','category':category.id}
        response = self.client().post('/questions',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        payload = {'previous_questions':[],'quiz_category':categor.format()}
        response = self.client().post('/quizzes',json=payload)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['question'],'test ?')
        
# Make the tests conveniently executable
if __name__ == "__main__" :
    unittest.main()