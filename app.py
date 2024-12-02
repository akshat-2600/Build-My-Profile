from flask import Flask , request , redirect , render_template , url_for
import mysql.connector
import os
import uuid

#Configure Flask app
app = Flask(__name__)

#Configure MYSQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ATM263014@atm",
    database="portfolio_db"

)

cursor = db.cursor()

# Directory to store uploaded files
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



#Route to display form
@app.route("/")
def index():
    return render_template("form.html")


#Route to handle form submission and save data to MYSQL
@app.route("/submit" , method=["POST"])
def submit():
    full_name = request.form["fullName"]
    email = request.fom["email"]
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

    

    #Handle Profile Picture Upload
    profile_picture = request.files["profilePicture"]
    filename = None
    if profile_picture:
        filename = os.path.join(app.config["UPLOAD_FOLDER"], profile_picture.filename)
        profile_picture.save(filename)

    
    #Generate a unique URL identifier
    unique_id = str(uuid.uuid4())

    #Insert the form data into the database
    query = """
    INSERT INTO portfolios (fullName, email, phone, birthdate, address, summary, skills, degree, institution, 
                            gradYear, grades, certificationName, certifyingAuthority, certificationDate, certificationLink, 
                            company, jobTitle, duration, description, languages, languageProficiency, 
                            projectTitle, projectDescription, technologiesUsed, projectLink, achievements, 
                            linkedin, github, personalWebsite, profilePicture)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """        

    cursor.execute(query, (full_name, email, phone, birthdate, address, summary, skills, degree, institution, grad_year, 
                           grades, certification_name, certifying_authority, certification_date, certification_link, 
                           company, job_title, duration, description, languages, language_proficiency, project_title, 
                           project_description, technologies_used, project_link, achievements, linkedin, github, 
                           personal_website, filename))
    
    db.commit()

    #Redirect user to their unique portfolio URL
    return redirect(url_for("portfolio" , unique_id=unique_id))


#Route to display portfolio using unique URL
@app.route("/portfolio/<unique_id>")
def portfolio(unique_id):
    #Fetch the user's portfolio dat from the database
    query = "SELECT * FROM portfolios WHERE id = (SELECT id FROM portfolios WHERE inique_id = %s)"
    
    cursor.execute(query , (unique_id,))
    portfolio_data = cursor.fetchone()


    if portfolio_data:
        return render_template("portfolio.html" , **portfolio_data)
    else:
        return "Portfolio not found" , 404
    





if __name__ == "__main__":
    app.run(port = 8080 , debug=True)