import json
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions
from ibm_watson import LanguageTranslatorV3

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://mmm79:M6901379mmm@mmm79.mysql.pythonanywhere-services.com/mmm79$comments"

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# bekop88804@toudrum.com email macekob471@chatich.com

def getTextByAudio(audio_f):

    # Insert API Key in place of
    # 'YOUR UNIQUE API KEY'
    authenticator = IAMAuthenticator('D9wd7ur-TAJNTjocitJqjLIoCedsGB7zJsKRtMLHyWLd')
    service = SpeechToTextV1(authenticator = authenticator)

    #Insert URL in place of 'API_URL'
    service.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/7bf40b64-05cd-4672-ad42-570fc09c73fa')

    file = open('/home/mmm79/mysite/w.mp3','rb')
    obj = service.recognize(
                audio=file,
                content_type='audio/mp3',
                model='en-US_NarrowbandModel').get_result()

    dic = json.loads(
            json.dumps(
                obj, indent=4))

    print(dic)
    # Stores the transcribed text
    str = ""

    while bool(dic.get('results')):
        str = dic.get('results').pop().get('alternatives').pop().get('transcript')+str[:]

    return str

"""

#    **Natural Language Understanding**




https://cloud.ibm.com/catalog/services/natural-language-understanding"""


def getNLU(str):
    NLU_apikey = 'nLmydTwLDwW9M0RrzN1FoAajfhO-MoQ454HBRf2-iPAt'
    NLU_url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/dd5dd53e-0925-4772-945a-e5f7eeb18eba'

    NLU_authenticator = IAMAuthenticator(NLU_apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=NLU_authenticator
    )

    natural_language_understanding.set_service_url(NLU_url)

    response = natural_language_understanding.analyze(
        text=str,
        features=Features(keywords=KeywordsOptions(sentiment=True,emotion=True,limit=2))).get_result()

    return json.dumps(response, indent = 4, ensure_ascii=False)


"""# **Language Translation part**

https://cloud.ibm.com/catalog/services/language-translator
"""


def getTranslation(str, model_id):
    LT_API = 'KnaSJk4AiMuNwldvuoWOJFMmClDFODj0gZX1N4E-xb2i'
    LT_URL = 'https://api.us-south.language-translator.watson.cloud.ibm.com/instances/1a6ea051-f892-4b6e-9c00-51e638f97b53'

    LT_authenticator = IAMAuthenticator(LT_API)
    language_translator = LanguageTranslatorV3(
        version='2020-01-01',
        authenticator=LT_authenticator
    )

    language_translator.set_service_url(LT_URL)
    language_translator.set_disable_ssl_verification(True)


    translation = language_translator.translate(
        text=str,
        model_id=model_id).get_result()
    return json.loads(json.dumps(translation, indent=4))


class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    movie = db.Column(db.Integer)


class Movie(db.Model):

    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    year = db.Column(db.Integer)
    url = db.Column(db.String(1024))



@app.route("/allComments", methods=["GET", "POST"])
def index_comments():

    print(db.select([Comment]).where(Comment.movie == 1))

    if request.method == "POST":
        return render_template("main_page.html", comments=Comment.query.all(),
            movies=Movie.query.all(), allComments = db.select([Comment]).where(Comment.movie == 1))



@app.route("/", methods=["GET", "POST"])
def index():

    return render_template("main_page.html", comments=Comment.query.all(), movies=Movie.query.all())




@app.route("/voice", methods=["GET", "POST"])
def index_voice():

    myfile = request.form['myfile']
    text = getTextByAudio(myfile)
    comment = Comment(content= text, movie=1)


    nlu_result = getNLU(text)
    print(nlu_result)
    cherk = float(nlu_result.split("anger")[1].split(":")[1].split("}")[0])
    print(cherk)
    if cherk < 0.4:
        db.session.add(comment)
        db.session.commit()
        db.session.close()
    return redirect(url_for('index'))


comment_movie = ""

@app.route("/postComment", methods=["POST"])
def post_comment():

    comment_movie = request.form['comment_movie']
    print(comment_movie)
    print(request.form['movie_id'])

    com = Comment(content=comment_movie, movie=request.form['movie_id'])
    # Check if comment has NOT that much Anger
    nlu_result = getNLU(comment_movie)
    print(nlu_result)
    cherk = float(nlu_result.split("anger")[1].split(":")[1].split("}")[0])
    print(cherk)
    if cherk < 0.4:
        db.session.add(com)
        db.session.commit()
        db.session.close()
    return redirect(url_for('index'))


@app.route("/translate", methods=["POST"])
def index_tr():

    translated_text = ""
    translate_comment = request.form['translate_comment']
    print(translate_comment)

    if request.form['tr_sp'] != None:
        tr_sp = request.form['tr_sp']
        print(tr_sp)
        translated_text = getTranslation(translate_comment, 'en-es')
    else:
        tr_ru = request.form['tr_ru']
        print(tr_ru)
        translated_text = getTranslation(translate_comment, 'en-he')

    translated_text = translated_text.split("translation:")[1].split("}")[0]
    return render_template("main_page.html", comments=Comment.query.all(), movies=Movie.query.all(), translated_text=translated_text)






