import os
from re import search
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection[start:end]]

  return questions


def format_categories(categories):
  categories_dict = {}
  for category in categories:
    categories_dict[category.id] = category.type

  return categories_dict


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins.
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  # Cors headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  Endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    formated_categories = format_categories(categories)

    return jsonify({
      'success': True,
      'categories': formated_categories
    })

  '''
  Endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_paginated_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    # abort 404 if request is beyond valid pages
    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.order_by(Category.id).all()
    formated_categories = format_categories(categories)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'current_category': "All",
      'categories': formated_categories
    })

  '''
  Endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)

    try:
      question.delete()

      return jsonify({
        'success': True,
        'id': question_id
      })

    except:
      abort(422)

  '''
  Endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_and_search_question():
    body = request.get_json()

    if body is None:
      abort(400)

    search_term = body.get('searchTerm', None)
    # perform search for questions if searchTerm is in request body
    if search_term:
      selection = Question.query.filter(
        Question.question.ilike('%{}%'.format(search_term))
        ).all()

      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': 'All'
      })

    # create new question if searchTerm is not in request body
    else:
      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)

      if (question is None or answer is None or
            difficulty is None or category is None):
        abort(400)

      try:
        new_question = Question(question, answer, category, difficulty)
        new_question.insert()

        return jsonify({
          'success': True
        })

      except:
        abort(422)

  '''
  GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    current_category = Category.query.filter(
      Category.id == category_id
    ).one_or_none()

    if current_category is None:
      abort(404)

    selection = Question.query.filter(
      Question.category == category_id
    ).all()
    current_questions = paginate_questions(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'current_category': current_category.type
    })

  '''
  POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_next_question():
    body = request.get_json()

    if body is None:
      abort(400)
    
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', {'id': 0})


    if quiz_category['id'] == 0:
      question = Question.query.filter(
        Question.id.not_in(previous_questions)
      ).first()

    else:
      category_check = Category.query.filter(
        Category.id == quiz_category['id']
      ).one_or_none()

      if category_check is None:
        abort(404)

      question = Question.query.filter(
        Question.id.not_in(previous_questions),
        Question.category == quiz_category['id']
      ).first()

    if question:
      question = question.format()

    return jsonify({
      'success': True,
      'question': question
    })

  '''
  Error handlers for all expected errors. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
      }), 500
  
  return app

    