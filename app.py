from flask import Flask , request , render_template , url_for

app = Flask(__name__)

@app.route("/")
def form():
    return render_template("portfolio.html")




if __name__ == "__main__":
    app.run(port = 8080 , debug=True)