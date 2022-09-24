import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request,questions):
    page= request.args.get("page",1, type=int)
    start_index= (page-1) * QUESTIONS_PER_PAGE
    stop_index= start_index + QUESTIONS_PER_PAGE
    return questions[start_index:stop_index]




def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    
    """
    CORS(app, resources={r"/*":{"origin":"*"}})
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories',methods=["GET"])
    def get_categories():
        try:

            categories= Category.query.all()
            categories_format={category.format()['id']:category.format()['type'] for category in categories}

            return jsonify({
                "success": True,
                "categories": categories_format
            })
        except:
            abort(400)


    @app.route("/questions",methods=["GET"])
    def get_questions():
        try:


            page = request.args.get("page",1,type=int)
            questions= Question.query.all()

            # insert the list of all the questions in an array
            question_list=[question.format() for question in questions]
            # paginate so only the questions in the current page are returned
            current_questions= paginate(request,question_list)
            
            if len(current_questions)== 0:
                abort(404)

        
            # get categories
            categories= Category.query.all()
            categories_format={category.format()['id']:category.format()['type'] for category in categories}
            
            # # current category is the category of the first question
            currentCategoryId= Question.query.filter(Question.question==current_questions[0]["question"]).first().category
            currentCategory= Category.query.filter(Category.id==currentCategoryId).first().type

            return jsonify({
                "success":True,
                "questions": current_questions,
                "totalQuestions":len(question_list),
                "categories":categories_format,
                "currentCategory": currentCategory,
                "page": page
                })
        except:
            abort(400)



    @app.route("/questions/<int:question_id>",methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id==question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            try:
                question.delete()
                return get_questions()
            except:
                abort(400)



    @app.route("/questions",methods=["POST"])
    def new_questions():
        try:

      
            body = request.get_json()
            question_text= body.get("question")
            answer_text= body.get("answer")
            difficulty= body.get("difficulty")
            category= body.get("category")
            
            search_term= body.get("searchTerm")
            if search_term:
                selections= Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()
                if len(selections)==0:
                    abort(404)
                else:

                    formatted_question=[question.format() for question in selections]

                    questions=paginate(request,formatted_question)


                    # # current category is the category of the first question
                    currentCategoryId= Question.query.filter(Question.question==formatted_question[0]["question"]).first().category
                    currentCategory= Category.query.filter(Category.id==currentCategoryId).first().type


                    return jsonify({"success":True,"questions":questions,"totalQuestions":len(formatted_question),"currentCategory":currentCategory})
            else:

                # POST for creating new question
            
                question = Question(question=question_text, category=category, difficulty=difficulty, answer=answer_text)

                question.insert()

                return get_questions()
        except:
            abort(400)



    @app.route("/categories/<int:category_id>/questions")
    def get_by_category(category_id):
        category = Category.query.filter(Category.id==category_id).one_or_none()
        if category is None :
            abort(404)

        try:
            selection = Question.query.filter(Question.category==category_id).all()
            formatted_questions=[question.format() for question in selection]
            current_questions= paginate(request,formatted_questions)
            return jsonify({"success":True,"totalQuestions":len(selection),"currentCategory":category.type,"questions":current_questions})
        except:
            abort(400)

  


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        try:

            body = request.get_json()
            previous_questions=body.get("previous_questions")
            quiz_category= body.get("quiz_category")
            quiz_category_id= quiz_category["id"]

            if not("previous_questions" in body and "quiz_category" in body):
                abort(422)

            # select all questions that belong to the category
            if quiz_category_id:
                    
                selection = Question.query.filter(Question.category==quiz_category_id).all()
            else:
                selection= Question.query.all()

            # format the selected questions
            format_selected= [question.format() for question in selection]

            # select only the ones that are not in the previous questions
            possible_question = [f_q for f_q in format_selected if f_q["id"] not in previous_questions]    

            if len(possible_question) == 0:
                selected_question= None
            else:

                selected_question = random.choice(possible_question)
        
            return jsonify({"question":selected_question,"success":True})
        
        except:
            abort(400)

        

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({"success": False,"error": 400,"message": "bad request"}),400)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({"success":False,"error":405,"message":"method not allowed"}),405)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({"success":False,"error":404,"message":"not found"}),404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({"success":False,"error":"unprocessable","message":"unprocessable"}),422)

    return app



