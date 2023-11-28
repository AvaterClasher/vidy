import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import mindsdb_sdk
from flask_cors import CORS
import threading

# Create the Flask app
app = Flask(__name__)
# Initialize CORS with your app
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:5000"}})

# Load the environment variables from the .env file
load_dotenv()

# Check if the environment variables are set
if os.environ.get('MINDSDB_EMAIL') is None:
    raise Exception('Please set the MINDSDB_EMAIL environment variable')
if os.environ.get('MINDSDB_PASSWORD') is None:
    raise Exception(
        'Please set the MINDSDB_PASSWORD environment variable')

# Connect to MindsDB Cloud server
try:
    server = mindsdb_sdk.connect(login=os.environ.get(
        'MINDSDB_EMAIL'), password=os.environ.get('MINDSDB_PASSWORD'))
    print("Connected to MindsDB Cloud server")
except:
    raise Exception("Check your internet connection or mindsdb credentials")

# Create project if not exists
try:
    project = server.get_project('vidy')
    print("Project Vidy already exists")
except:
    project = server.create_project('vidy')
    print("Project Vidy created")

# Add data sources if not exists
try:
    # Check if the environment variables are set
    if os.environ.get('YOUTUBE_API_KEY') is None:
        raise Exception(
            'Please set the YOUTUBE_API_KEY environment variable')
    # Create the database
    mindsdb_youtube = server.create_database(name='mindsdb_youtube', engine='youtube', connection_args={
        'youtube_api_token': os.environ.get('YOUTUBE_API_KEY')})
    print("Database mindsdb_youtube created")
except:
    mindsdb_youtube = server.get_database('mindsdb_youtube')
    print("Database mindsdb_youtube already exists")

def create_model(name: str, engine: str, predict: str, options: dict):
    from time import sleep
    # check model is exist or not
    try:
        # Create the model
        model = project.models.create(
            name=name,
            engine=engine,
            predict=predict,
            options=options
        )
        print(f"Model {name} created")
        # Wait for the model to be trained
        while model.get_status() != 'complete':
            sleep(1)
            print("Training the model...")
        return model
    except:
        # Get the model
        print(f"Model {name} already exists")
        return project.models.get(name)

# Create sentiment_classifier_model
sentiment_classifier_model = create_model(name='sentiment_classifier_model',
                                          engine='huggingface',
                                          predict='sentiment',
                                          options={
                                              'task': 'text-classification',
                                              'model_name': 'cardiffnlp/twitter-roberta-base-sentiment',
                                              'input_column': 'comment',
                                              'labels': ['negative', 'neutral', 'positive']
                                          })

# Create spam classifier model
spam_classifier_model = create_model(name='spam_classifier_model',
                                     engine='huggingface',
                                     predict='spam',
                                     options={
                                            'task': 'text-classification',
                                            'model_name': 'mrm8488/bert-tiny-finetuned-sms-spam-detection',
                                            'input_column': 'comment',
                                            'labels': ['false', 'true']
                                     })

# Create text summarization model
text_summarization_model = create_model(name='text_summarization_model',
                                        engine='openai',
                                        predict='comment_summary',
                                        options={
                                            'prompt_template': "provide an informative summary of the comments comments:{{comments}} using full sentences",
                                            'api_key': os.environ.get('OPENAI_API_KEY')
                                        })

# Create keyword recommendation model
recommendation_model = create_model(name='recommendation_model',
                                    engine='openai',
                                    predict='recommendation',
                                    options={
                                            'prompt_template': "Based on the comments from YouTube videos, strictly tell me the topic names that a YouTuber can consider to grow their channel. Example: 'Python' if peoples are talking about python. comments:{{comments}}",
                                            'api_key': os.environ.get('OPENAI_API_KEY')
                                    })

# response dictionary
response = {}

def get_sentiments(data):
    """
    Extracts the sentiments from the comments
    
    Args:
        data (Table): comments
        example: Table with columns ['display_name', 'username', 'comment']
    """
    # Predict sentiments
    sentiment_result = sentiment_classifier_model.predict(data)
    # store the sentiments in response dictionary
    sentiment_counts = sentiment_result['sentiment'].value_counts()
    response["sentiments"] = {
        "positive": int(sentiment_counts.get('positive', 0)),
        "neutral": int(sentiment_counts.get('neutral', 0)),
        "negative": int(sentiment_counts.get('negative', 0))
    }

def get_spams(data):
    """
    detects the spams in the comments
    
    Args:
        data (Table): comments
        example: Table with columns ['display_name', 'username', 'comment']
    """
    # Predict spams
    spam_result = spam_classifier_model.predict(data)
    # store the spams in response dictionary
    spam_counts = spam_result['spam'].value_counts()
    response["spams"] = int(spam_counts.get('true', 0))

def get_summarization(data):
    """makes a summary of the comments

    Args:
        data (dict): comments
        example: {'comments': 'comment1 comment2 comment3'}
    """
    # predict the summary
    summarizer_result = text_summarization_model.predict(
        data=data)
    # store the summary in response dictionary
    response["comment_summary"] = str(summarizer_result['comment_summary'][0])

def get_recommendation(data):
    """makes a summary of the comments

    Args:
        data (dict): comments
        example: {'comments': 'comment1 comment2 comment3'}
    """
    # predict the recommendation
    recommendation_result = recommendation_model.predict(
        data=data)
    # store the recommendation in response dictionary
    response["recommendation"] = str(
        recommendation_result['recommendation'][0])

@app.route('/api/youtube', methods=['GET'])
def get_vidy():
    # Get args from request url
    youtube_video_id = request.args.get('youtube_video_id')
    max_comments_limit = int(request.args.get('limit', 10))
    sentiment = request.args.get('sentiment', 'false')
    spam = request.args.get('spam', 'false')
    comment_summary = request.args.get('comment_summary', 'false')
    recommendation = request.args.get('recommendation', 'false')
    
    # Get the comments table from the database
    comments_table = mindsdb_youtube.get_table('get_comments').filter(
        youtube_video_id=youtube_video_id).limit(max_comments_limit)
    
    if comment_summary == 'true' or recommendation == 'true':
        comments = comments_table.fetch()
        merged_comments = ' '.join(comments['comment'].tolist())
    
    # threads list
    threads = []
    # Reset response dictionary
    global response
    response = {}
    # predict sentiments
    if sentiment == 'true':
        t1 = threading.Thread(target=get_sentiments, args=(comments_table,))
        threads.append(t1)
        t1.start()

    # predict spams
    if spam == 'true':
        t2 = threading.Thread(target=get_spams, args=(comments_table,))
        threads.append(t2)
        t2.start()

    # predict comment summary
    if comment_summary == 'true':
        t3 = threading.Thread(target=get_summarization, args=(
            {'comments': merged_comments},))
        threads.append(t3)
        t3.start()

    # predict recommendation
    if recommendation == 'true':
        t4 = threading.Thread(target=get_recommendation,
                              args=({'comments': merged_comments},))
        threads.append(t4)
        t4.start()

    # wait for the threads to finish
    for thread in threads:
        thread.join()

    return jsonify(response)

if __name__ == '__main__':
    app.run()