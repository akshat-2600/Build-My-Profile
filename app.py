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
        
        filename = secure_filename(profile_picture.filename)
        
        filename = f"{uuid.uuid4()}_{filename}"
        
        profile_picture_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        profile_picture.save(profile_picture_filename)
        #profile_picture_filename = profile_picture_filename.replace("\\", "/")
     

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
            portfolio_data['profile_picture'] = url_for('static', filename='uploads/' + os.path.basename(portfolio_data['profile_picture_filename']))

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

















'''
import os
import mysql.connector
from flask import Flask, request, redirect, render_template, url_for
import uuid
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Set your DATABASE_URL
import os
import mysql.connector

# Use DATABASE_URL from environment variables or a default placeholder
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://root:snuyLbhWjpIlZpRaRTfHafrpjjTgraLd@junction.proxy.rlwy.net:13573/railway")

# Parse the DATABASE_URL into components
def parse_database_url(url):
    url = url.replace("mysql://", "")  # Adjust prefix to match the standard
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


@app.route("/submit", methods=["POST"])
def submit():
    # Collect form data
    fullName = request.form["fullName"]
    if not fullName:
        return "Full name is required", 400

    email = request.form["email"]
    phone = request.form["phone"]
    birthdate = request.form["birthdate"]
    address = request.form["address"]
    summary = request.form["summary"]
    skills = request.form["skills"]
    degree = request.form["degree"]
    institution = request.form["institution"]
    grad_year = request.form["gradYear"]
    grades = request.form["grades"]
    certification_name = request.form["certificationName"]
    certifying_authority = request.form["certifyingAuthority"]
    certification_date = request.form["certificationDate"]
    certification_link = request.form["certificationLink"]
    company = request.form["company"]
    job_title = request.form["jobTitle"]
    duration = request.form['duration']
    description = request.form['description']
    languages = request.form['languages']
    language_proficiency = request.form['languageProficiency']
    project_title = request.form['projectTitle']
    project_description = request.form['projectDescription']
    technologies_used = request.form['technologiesUsed']
    project_link = request.form['projectLink']
    achievements = request.form['achievements']
    linkedin = request.form['linkedin']
    github = request.form['github']
    personal_website = request.form['personalWebsite']

    # Handle Profile Picture Upload
    profile_picture = request.files.get("profile_picture")
    profile_picture_filename = None
    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        filename = f"{uuid.uuid4()}_{filename}"
        profile_picture_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        profile_picture.save(profile_picture_path)
        profile_picture_filename = f"uploads/{filename}"

    # Handle certificationDate
    try:
        certification_date = datetime.strptime(certification_date, '%Y-%m-%d').strftime('%Y-%m-%d') if certification_date else None
    except ValueError:
        certification_date = None

    # Generate a unique URL identifier
    unique_id = str(uuid.uuid4())

    # Create user data dictionary
    user_data = {
        "unique_id": unique_id,
        "fullName": fullName,
        "email": email,
        "phone": phone,
        "birthdate": birthdate,
        "address": address,
        "summary": summary,
        "skills": skills,
        "degree": degree,
        "institution": institution,
        "gradYear": grad_year,
        "grades": grades,
        "certificationName": certification_name,
        "certifyingAuthority": certifying_authority,
        "certificationDate": certification_date,
        "certificationLink": certification_link,
        "company": company,
        "jobTitle": job_title,
        "duration": duration,
        "description": description,
        "languages": languages,
        "languageProficiency": language_proficiency,
        "projectTitle": project_title,
        "projectDescription": project_description,
        "technologiesUsed": technologies_used,
        "projectLink": project_link,
        "achievements": achievements,
        "linkedin": linkedin,
        "github": github,
        "personalWebsite": personal_website,
        "profilePicture": profile_picture_filename
    }

    # Save user data to a JSON file
    user_file_path = os.path.join(DATA_FOLDER, f"{unique_id}.json")
    with open(user_file_path, "w") as f:
        json.dump(user_data, f)

    # Redirect to portfolio
    return redirect(url_for("portfolio", unique_id=unique_id))

@app.route("/portfolio/<unique_id>")
def portfolio(unique_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch user data
        query = "SELECT * FROM portfolios WHERE unique_id = %s"
        cursor.execute(query, (unique_id,))
        portfolio_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if portfolio_data:
            return render_template("portfolio.html", **portfolio_data)
        else:
            return "Portfolio not found", 404
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(debug=True)


'''













'''
from flask import Flask, request, redirect, render_template, url_for
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import mysql.connector
from sqlalchemy import create_engine

# Load MySQL credentials from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

MYSQL_HOST = config['MYSQL_HOST']
MYSQL_USER = config['MYSQL_USER']
MYSQL_PASSWORD = config['MYSQL_PASSWORD']
MYSQL_DB = config['MYSQL_DB']



# Configure Flask app
app = Flask(__name__)

# Set your DATABASE_URL (make sure you add your Railway MySQL URL here)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://root:snuyLbhWjpIlZpRaRTfHafrpjjTgraLd@junction.proxy.rlwy.net:13573/railway")

# Parse the DATABASE_URL into components
def parse_database_url(url):
    # Remove the 'mysql+mysqlconnector://' prefix
    url = url.replace("mysql+mysqlconnector://", "")
    # Split into components: username:password@host:port/database
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

# Connect to MySQL using parsed information
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

@app.route("/test_db")
def test_db():
    try:
        # Test the connection
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        connection.close()
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"


db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
if db.is_connected():
    print("Database connection successful!")
else:
    print("Failed to connect to the database.")



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

# Route to display form
@app.route("/")
def index():
    return render_template("form.html")

# Route to handle form submission and save data
@app.route("/submit", methods=["POST"])
def submit():
    fullName = request.form["fullName"]
    if not fullName:
        return "Full name is required", 400

    email = request.form["email"]
    phone = request.form["phone"]
    birthdate = request.form["birthdate"]
    address = request.form["address"]
    summary = request.form["summary"]
    skills = request.form["skills"]
    degree = request.form["degree"]
    institution = request.form["institution"]
    grad_year = request.form["gradYear"]
    grades = request.form["grades"]
    certification_name = request.form["certificationName"]
    certifying_authority = request.form["certifyingAuthority"]
    certification_date = request.form["certificationDate"]
    certification_link = request.form["certificationLink"]
    company = request.form["company"]
    job_title = request.form["jobTitle"]
    duration = request.form['duration']
    description = request.form['description']
    languages = request.form['languages']
    language_proficiency = request.form['languageProficiency']
    project_title = request.form['projectTitle']
    project_description = request.form['projectDescription']
    technologies_used = request.form['technologiesUsed']
    project_link = request.form['projectLink']
    achievements = request.form['achievements']
    linkedin = request.form['linkedin']
    github = request.form['github']
    personal_website = request.form['personalWebsite']

    # Handle Profile Picture Upload
    profile_picture = request.files.get("profilePicture")
    profile_picture_filename = None
    if profile_picture:
        # Ensure the filename is safe
        filename = secure_filename(profile_picture.filename)
        
        # Add a unique identifier to the filename to avoid conflicts
        filename = f"{uuid.uuid4()}_{filename}"
        
        # Create the absolute path for saving the file
        profile_picture_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        # Save the file
        profile_picture.save(profile_picture_filename)

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

    # Store the form data in a JSON file
    user_data = {
        "unique_id": unique_id,
        "fullName": fullName,
        "email": email,
        "phone": phone,
        "birthdate": birthdate,
        "address": address,
        "summary": summary,
        "skills": skills,
        "degree": degree,
        "institution": institution,
        "gradYear": grad_year,
        "grades": grades,
        "certificationName": certification_name,
        "certifyingAuthority": certifying_authority,
        "certificationDate": certification_date,  # This is now a string
        "certificationLink": certification_link,
        "company": company,
        "jobTitle": job_title,
        "duration": duration,
        "description": description,
        "languages": languages,
        "languageProficiency": language_proficiency,
        "projectTitle": project_title,
        "projectDescription": project_description,
        "technologiesUsed": technologies_used,
        "projectLink": project_link,
        "achievements": achievements,
        "linkedin": linkedin,
        "github": github,
        "personalWebsite": personal_website,
        "profilePicture": profile_picture_filename
    }

    # Save user data to a JSON file
    user_file_path = os.path.join(DATA_FOLDER, f"{unique_id}.json")
    with open(user_file_path, "w") as f:
        json.dump(user_data, f)

    # Redirect user to their unique portfolio URL
    return redirect(url_for("portfolio", unique_id=unique_id))

# Route to display portfolio using unique URL
@app.route("/portfolio/<unique_id>")
def portfolio(unique_id):
    # Fetch the user's portfolio data from the file
    user_file_path = os.path.join(DATA_FOLDER, f"{unique_id}.json")

    if os.path.exists(user_file_path):
        with open(user_file_path, "r") as f:
            portfolio_data = json.load(f)

        # Convert certificationDate back to datetime if needed
        if portfolio_data["certificationDate"]:
            portfolio_data["certificationDate"] = datetime.strptime(portfolio_data["certificationDate"], '%Y-%m-%d')

        # Make sure the profile picture is passed correctly
        if portfolio_data['profilePicture']:
            portfolio_data['profilePicture'] = url_for('static', filename='uploads/' + os.path.basename(portfolio_data['profilePicture']))

        return render_template("portfolio.html", **portfolio_data)
    else:
        return "Portfolio not found", 404

# Route to display all users data in admin panel
@app.route("/admin/users")
def show_users():
    # Connect to the MySQL database using credentials from config.json
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    if db.is_connected():
        print("Database connection successful!")
    else:
        print("Failed to connect to the database.")
    
    cursor = db.cursor()

    # Query the database to get all users
    query = "SELECT * FROM portfolios"
    cursor.execute(query)
    users_data = cursor.fetchall()

    # Prepare column names for the table
    portfolio_columns = ["profile_picture", "id", "unique_id", "fullName", "email", "phone", "birthdate", "address", "summary", "skills", 
                         "degree", "institution", "gradYear", "grades", "certificationName", "certifyingAuthority", 
                         "certificationDate", "certificationLink", "company", "jobTitle", "duration", "description", 
                         "languages", "languageProficiency", "projectTitle", "projectDescription", "technologiesUsed", 
                         "projectLink", "achievements", "linkedin", "github", "personalWebsite"]

    # Create a list of dictionaries from the fetched data
    users_list = []
    for user in users_data:
        user_dict = dict(zip(portfolio_columns, user))
        user_dict["profile_picture"] = str(user_dict["profile_picture"])  # Convert to string
        users_list.append(user_dict)

    # Close the database connection
    cursor.close()
    db.close()

    # Render the data in a template
    return render_template("show_users.html", users=users_list)


if __name__ == "__main__":
    app.run(port=8080, debug=True)

'''