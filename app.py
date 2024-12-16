import os
import mysql.connector
from flask import Flask, request, redirect, render_template, url_for
import uuid
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api


app = Flask(__name__)



cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dcsgtgnbg'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '889146638363735'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', '9Nx3D-lR8TfKHuEeyveIttmvFQo')
)




UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


DATA_FOLDER = "user_data"
app.config["DATA_FOLDER"] = DATA_FOLDER


if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql://root:snuyLbhWjpIlZpRaRTfHafrpjjTgraLd@junction.proxy.rlwy.net:13573/railway"
)


def parse_database_url(url):
    url = url.replace("mysql://", "")
    user_pass, host_db = url.split('@')
    username, password = user_pass.split(':')
    host, port_db = host_db.split(':')
    port, database = port_db.split('/')
    return {
        "user": username,
        "password": password,
        "host": host,
        "port": int(port),
        "database": database
    }


def get_db_connection():
    db_config = parse_database_url(DATABASE_URL)
    connection = mysql.connector.connect(
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"]
    )
    return connection


def create_tables():
    try:
        
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unique_id VARCHAR(36) NOT NULL,
            full_name VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(20),
            birthdate DATE,
            address TEXT,
            summary TEXT,
            skills TEXT,
            degree VARCHAR(255),
            institution VARCHAR(255),
            grad_year INT,
            grades VARCHAR(50),
            certification_name VARCHAR(255),
            certifying_authority VARCHAR(255),
            certification_date DATE,
            certification_link TEXT,
            company VARCHAR(255),
            job_title VARCHAR(255),
            duration VARCHAR(100),
            description TEXT,
            languages TEXT,
            language_proficiency TEXT,
            project_title VARCHAR(255),
            project_description TEXT,
            technologies_used TEXT,
            project_link TEXT,
            achievements TEXT,
            linkedin TEXT,
            github TEXT,
            personal_website TEXT,
            profile_picture TEXT
        );
        """)

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

create_tables()


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():

    unique_id = str(uuid.uuid4())

    full_name = request.form["full_name"]
    if not full_name:
        return "Full name is required", 400

    email = request.form["email"]
    phone = request.form["phone"]
    birthdate = request.form["birthdate"]
    address = request.form["address"]
    summary = request.form["summary"]
    skills = request.form["skills"]
    degree = request.form["degree"]
    institution = request.form["institution"]
    grad_year = request.form["grad_year"]
    grades = request.form["grades"]
    certification_name = request.form["certification_name"]
    certifying_authority = request.form["certifying_authority"]
    certification_date = request.form["certification_date"]
    certification_link = request.form["certification_link"]
    company = request.form["company"]
    job_title = request.form["job_title"]
    duration = request.form["duration"]
    description = request.form["description"]
    languages = request.form["languages"]
    language_proficiency = request.form["language_proficiency"]
    project_title = request.form["project_title"]
    project_description = request.form["project_description"]
    technologies_used = request.form["technologies_used"]
    project_link = request.form["project_link"]
    achievements = request.form["achievements"]
    linkedin = request.form["linkedin"]
    github = request.form["github"]
    personal_website = request.form["personal_website"]




    profile_picture = request.files.get("profile_picture")
    profile_picture_url = None
    if profile_picture and profile_picture.filename:
        try:
            upload_result = cloudinary.uploader.upload(
                profile_picture,
                folder="portfolio_pictures",
                transformation=[
                    {'width': 400, 'height': 400, 'crop': 'fill'}
                ]
            )
            
            profile_picture_url = upload_result['secure_url']
        
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            profile_picture_url = None
    

        

    if certification_date:
        try:
            certification_date = datetime.strptime(certification_date, '%Y-%m-%d')
            certification_date = certification_date.strftime('%Y-%m-%d')
        except ValueError:
            certification_date = None
    

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO portfolios (
            unique_id, full_name, email, phone, birthdate, address, summary,
            skills, degree, institution, grad_year, grades,
            certification_name, certifying_authority, certification_date, certification_link,
            company, job_title, duration, description, languages, language_proficiency,
            project_title, project_description, technologies_used, project_link,
            achievements, linkedin, github, personal_website, profile_picture
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,%s
        )
        """
        cursor.execute(insert_query, (
            unique_id, full_name, email, phone, birthdate, address, summary,
            skills, degree, institution, grad_year, grades,
            certification_name, certifying_authority, certification_date, certification_link,
            company, job_title, duration, description, languages, language_proficiency,
            project_title, project_description, technologies_used, project_link,
            achievements, linkedin, github, personal_website, profile_picture_url
        ))
        connection.commit()

    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for("portfolio", unique_id=unique_id))


@app.route("/portfolio/<unique_id>")
def portfolio(unique_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM portfolios WHERE unique_id = %s"
        cursor.execute(query, (unique_id,))
        portfolio_data = cursor.fetchone()

        
        if not portfolio_data['profile_picture']:
            portfolio_data['profile_picture'] = 'default_profile_url'

        if portfolio_data:
            return render_template("portfolio.html", **portfolio_data)
        else:
            return "Portfolio not found", 404

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)
