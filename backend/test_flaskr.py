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
        self.database_path = "postgres://{}@{}/{}".format('postgres','localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """
 __________________________________________________________________________________________________       
    GET CATEGORIES
    ____________________________________________________________________________________________________       
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data["categories"])
        self.assertEqual(len(data["categories"]),6)
    
    def test_405_method_not_allowed(self):
        res = self.client().patch("/categories",json={"message":"not allowed"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data["success"],False)

    """
 __________________________________________________________________________________________________       
    GET QUESTIONS
    ____________________________________________________________________________________________________       
    """    
    def test_get_questions(self):
        res= self.client().get("/questions?page=1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data["questions"])
        self.assertEqual(data["page"],1)

    def test_400_bad_request_for_page_beyond_possible(self):
        res= self.client().get("/questions?page=1000")
        data= json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data["success"],False)

    """
 __________________________________________________________________________________________________       
    DELETE
    ____________________________________________________________________________________________________       
    """
    def test_delete_question_by_id(self):
        response = self.client().delete("/questions/21")
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["page"],1)


    def test_404_for_deleted_questions_not_present(self):
        response=self.client().delete("/questions/200")
        data= json.loads(response.data)
        self.assertEqual(response.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"not found")

    
  

    """
   ________________________________________________________________________________________________       
    SEARCH
    ____________________________________________________________________________________________________       
    """
    def test_search_question(self):
        response= self.client().post("/questions",json={"searchTerm":"name"})
        data= json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])

    def test_404_for_search_string_not_found(self):
        response = self.client().post("/question",json={"searchTerm":"bucket"})
        data = json.loads(response.data)
        self.assertEqual(response.status_code,404)
        self.assertEqual(data["success"],False)


    """
   ________________________________________________________________________________________________       
    GET QUESTIONS BY CATEGORY
    ____________________________________________________________________________________________________       
    """

    def test_get_questions_by_category(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertTrue(data["questions"])
        self.assertEqual(data["success"],True)

    def test_404_for_category_not_found(self):
        response = self.client().get("/categories/1000/questions")
        data = json.loads(response.data)
        self.assertEqual(response.status_code,404)
        self.assertEqual(data["success"],False)

    """
   ________________________________________________________________________________________________       
    QUIZZES
    ____________________________________________________________________________________________________       
    """

    def test_get_quiz(self):
        response = self.client().post("/quizzes", json={"previous_questions": [20], "quiz_category" : {"id":"4","type":"History"}})

        body = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertTrue(body["question"])


    def test_400_bad_request_for_quizzes(self):
        response= self.client().post("/quizzes")
        body = json.loads(response.data)
        self.assertEqual(response.status_code,400)
        self.assertEqual(body["success"],False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

