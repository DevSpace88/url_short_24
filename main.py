from flask import Flask, render_template, url_for, jsonify

import hashlib
from flask_pymongo import PyMongo
from datetime import datetime
import os
from flask_wtf import FlaskForm
from wtforms import StringField, validators

from dotenv import load_dotenv
load_dotenv()
import logging

logging.basicConfig(level=logging.INFO)

s3_bucket_name = os.environ['S3_BUCKET_NAME']

s3_bucket_name = os.environ['S3_BUCKET_NAME']
aws_region = os.environ['AWS_REGION']
s3_bucket_url = f'https://{s3_bucket_name}.s3.{aws_region}.amazonaws.com'

app = Flask(__name__)

app.static_url_path  = f'{s3_bucket_url}/static'

app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")


MONGO_URL = os.environ["MONGO_URL"]
app.config["MONGO_URI"] = MONGO_URL
mongo = PyMongo(app)

app.config['S3_BUCKET_URL'] = s3_bucket_url
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SERVER_NAME'] = os.environ['PROJECT_URL']

class LinkForm(FlaskForm):
    link = StringField('Link', [
        validators.Length(max=1000, message="Link must be less than 1000 characters"),
        validators.URL(message="Please enter a valid URL")
    ])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    short_url = None
    
    if mongo.db is None:
        return "Failed to connect to MongoDB", 500
    
    if form.validate_on_submit():
        original_url = form.link.data
        
        if original_url:
            original_url = original_url.strip()
        elif not original_url:
            return jsonify(error="Please enter a valid URL"), 400
        
        project_url = os.environ.get("PROJECT_URL", "")
        
        if project_url in original_url:
            return jsonify(error="This domain is not allowed. Please enter a valid URL"), 400
        
        existing_link = mongo.db.links.find_one({"original_url": original_url})
        
        if existing_link:
            short_url = url_for('redirect_to_original', url_slug=existing_link['slug'], _external=True)
            return jsonify(short_url=short_url)
        
        url_slug = hashlib.md5(original_url.encode()).hexdigest()[:6]
        
        while mongo.db.links.find_one({"slug": url_slug}):
            url_slug = hashlib.md5((original_url + url_slug).encode()).hexdigest()[:6]
        
        mongo.db.links.insert_one({"slug": url_slug, "original_url": original_url, "created_at": datetime.utcnow()})
        
        short_url = url_for('redirect_to_original', url_slug=url_slug, _external=True)
        
        return jsonify(short_url=short_url)
    
    else:
        print("Form Error")
    
    return render_template('index.html', form=form)



@app.route('/<url_slug>')
def redirect_to_original(url_slug):
    link = mongo.db.links.find_one({"slug": url_slug})
    if link:
        return render_template('interstitial.html', target_url=link['original_url'])
    else:
        return render_template('404.html'), 404

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=False)