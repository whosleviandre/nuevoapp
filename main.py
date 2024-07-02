from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = '_5#y2L"f4q8Z' 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/base")
def base():
    return render_template("base.html")

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Aquí deberías verificar el usuario y contraseña
        return render_template("login.html")
    return redirect(url_for("index"))


@app.route("/segura")
def segura():
    if 'username' in session:  
        return render_template("segura.html")
    else:
        return redirect(url_for("login"))



@app.route("/error")
def error():
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)
