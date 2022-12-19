from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def pagina_principal():
    return render_template('index.html')


@app.route("/calculadora")
def calculadora():
    return render_template('Calculadora.html')




if __name__ == "__main__":
    app.run(debug = True)
