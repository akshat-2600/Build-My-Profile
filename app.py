from flask import Flask, request, redirect, render_template, url_for
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import mysql.connector

# Load MySQL credentials from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

MYSQL_HOST = config['MYSQL_HOST']
MYSQL_USER = config['MYSQL_USER']
MYSQL_PASSWORD = config['MYSQL_PASSWORD']
MYSQL_DB = config['MYSQL_DB']

# Configure Flask app
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

