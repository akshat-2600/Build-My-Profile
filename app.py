import os
import mysql.connector
from flask import Flask, request, redirect, render_template, url_for
import uuid
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Directory to store uploaded files
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Directory to store user data (JSON files)
DATA_FOLDER = "user_data"
app.config["DATA_FOLDER"] = DATA_FOLDER

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Use DATABASE_URL from environment variables or a default placeholder
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql://root:snuyLbhWjpIlZpRaRTfHafrpjjTgraLd@junction.proxy.rlwy.net:13573/railway"
)

# Parse the DATABASE_URL into components
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

# Establish a database connection
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

# Create the necessary tables if they don't exist
def create_tables():
    try:
        # Establish the database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Create the `portfolios` table if it doesn't already exist
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

        # Commit the changes
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Ensure resources are closed properly
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Initialize the tables
create_tables()

# Route to display form
@app.route("/")
def index():
    return render_template("form.html")

# Route to handle form submission
@app.route("/submit", methods=["POST"])
def submit():
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




    # Handle Profile Picture Upload
    profile_picture = request.files.get("profile_picture")
    profile_picture_filename = None
    if profile_picture:
        # Generate a unique filename
        filename = secure_filename(profile_picture.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Save the file
        full_file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        profile_picture.save(full_file_path)
        
        # Store only the filename in the database, not the full path
        profile_picture_filename = unique_filename
        

    # Handle certificationDate
    if certification_date:
        try:
            certification_date = datetime.strptime(certification_date, '%Y-%m-%d')
        except ValueError:
            certification_date = None
    else:
        certification_date = None

    # Convert datetime to string (if needed)
    if certification_date:
        certification_date = certification_date.strftime('%Y-%m-%d')  # Convert to string format

    # Generate a unique URL identifier
    unique_id = str(uuid.uuid4())

    # Insert user data into the database
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
            achievements, linkedin, github, personal_website, profile_picture_filename
        ))
        connection.commit()

    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Redirect to portfolio
    return redirect(url_for("portfolio", unique_id=unique_id))

# Route to display portfolio
@app.route("/portfolio/<unique_id>")
def portfolio(unique_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM portfolios WHERE unique_id = %s"
        cursor.execute(query, (unique_id,))
        portfolio_data = cursor.fetchone()

        if portfolio_data['profile_picture']:
            portfolio_data['profile_picture'] = url_for('static', filename=f'uploads/{portfolio_data["profile_picture"]}')

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
