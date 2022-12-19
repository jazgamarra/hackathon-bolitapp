from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def pagina_principal():
    return render_template('index.html')

@app.route("/balance")
def balance():
    return render_template('balance.html')

@app.route("/ingresar_datos")
def ingresar_datos():
    return render_template('balance.html')

@app.route("/aprender")
def aprender():
    return render_template('balance.html')

@app.route("/login_page")
def login_page():
    return render_template('loginpage.html')


if __name__ == "__main__":
    app.run(debug = True)
