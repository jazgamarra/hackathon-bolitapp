from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def pagina_principal():
    return render_template('inicio.html')

@app.route("/balance")
def balance():
    return render_template('balance.html')

@app.route("/ingresar_datos")
def ingresar_datos():
    return render_template('ingreso_datos.html')

@app.route("/aprender")
def aprender():
    return render_template('aprender.html')

@app.route("/login_page")
def login_page():
    return render_template('index.html')

@app.route("/crear_cuenta")
def sign_up():
    return render_template('crear_cuenta.html')

@app.route("/inicio")
def inicio():
    return render_template('inicio.html')

@app.route("/quienes_somos")
def quienes_somos():
    return render_template('quienes_somos.html')

@app.route("/perfil")
def perfil():
    return render_template('perfil.html')

if __name__ == "__main__":
    app.run(debug = True)
