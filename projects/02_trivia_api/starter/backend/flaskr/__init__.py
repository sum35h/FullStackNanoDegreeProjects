import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
  page = request.args.get('page',1,type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_page = questions[start:end]

  return current_page

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {"origins": "*"}},
         supports_credentials=True)
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                          'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                          'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def fetch_categories():
    try:
      categories=Category.query.all()
      print(categories)

      #result = [category.format() for category in categories]
      idCategoryMap = {category.id:category.type for category in categories}
      return jsonify({"success":True,
     
      "categories": idCategoryMap
    })
    except Exception as e:
      print(e)
      abort(404)

  ''' 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def fetch_questions():
    try:
       selection = Question.query.all()
       current_page = paginate_questions(request,selection)
       categories ={c.id:c.type for c in Category.query.all()}
 
       if len(current_page)==0:
         abort(404)
       return jsonify({"success":True,
                         "questions":[current for current in current_page],
                         "totalQuestions":len(selection),"categories":categories,"currentCategory": None
                                  })
    except Exception as e:
      print(e)
      abort(400)

  ''' 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()

      return jsonify({'success':True})
    except:
      abort(400)

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():
    try:
      payload = request.get_json()

      question = Question(answer=payload.get('answer',None),
      category=payload.get('category',None),
      difficulty=payload.get('difficulty',None),
      question=payload.get('question',None))
      question.insert()
      
      return jsonify({"success":True,"id":question.id})
    except Exception as e:
      print(e)
      abort(400)

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_question():
    data = request.get_json()
    searchTerm = data.get('searchTerm')

    questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()

    return jsonify({"success":True,
                    "questions":paginate_questions(request,questions),
                     "totalQuestions":len(questions),
                     "currentCategory":None})
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def fetch_questions_of_category(id):
   try:
    category = Category.query.get(id)
    questions = Question.query.filter(Question.category==str(id)).all()
    
    return jsonify({"success":True,
                      "questions":[question.format() for question in questions],
                      "totalQuestions":len(questions),"currentCategory": category.type
                              })
   except:
     abort(400)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def play_quiz():
   
   data = request.get_json()
   print('data=',data)
   
   quiz_category = data.get('quiz_category')
   id = quiz_category['id']
   if id == 0:
    questions = Question.query.all()
   else:
    questions = Question.query.filter(Question.category==id).all()
   previous_questions = data.get('previous_questions')
   remaining_questions = [question.format() for question in questions if question.id not in previous_questions]
   print(remaining_questions)
   if len(remaining_questions)>1:
    print("len=",len(remaining_questions))
    random_index = random.randint(0,len(remaining_questions)-1)
    print('--',random_index)
    question = remaining_questions[random_index]
    
   elif len(remaining_questions)==1:
    question=remaining_questions.pop()
   else:
    question = None
   return jsonify({"success":True,
   "previous_question":previous_questions,
   "question":question,
   "quiz_category":quiz_category})

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({"success":False,
                    "error":400,
                    "message":"Bad Request"}),400
             
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({"success":False,
                    "error":404,
                    "message":"Not found"}),404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({"success":False,
                    "error":422,
                    "message":"Unprocessable Entity"}),422

  @app.errorhandler(500)
  def interal_server_error(error):
    return jsonify({"success":False,
                    "error":500,
                    "message":"Internal Server Error"}),500

  return app

    