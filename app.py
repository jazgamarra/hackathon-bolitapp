from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy import func
import random


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

categorias_validas_ingreso = ['salario', 'extras']
categorias_validas_egreso = ['vivienda', 'deudas', 'servicios', 'supermercado', 'movilidad', 'entretenimiento']

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    telefono = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)

    def __init__(self, nombre, telefono, password):
        self.nombre = nombre
        self.telefono = telefono
        self.password = password

class Transactions (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaccion = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)

    def __init__(self, transaccion, monto, categoria, telefono):
        self.transaccion = transaccion
        self.monto = monto
        self.categoria = categoria
        self.telefono = telefono

def calcular_saldo(telefono):
    transacciones_ingresos = db.session.query(Transactions).filter_by(
        telefono=telefono).filter_by(transaccion='ingreso')
    saldo = 0
    for transaccion in transacciones_ingresos:
        saldo = saldo + transaccion.monto

    transacciones_egresos = db.session.query(Transactions).filter_by(telefono=telefono).filter_by(transaccion='egreso')

    for transaccion in transacciones_egresos:
        saldo = saldo - transaccion.monto

    return saldo

def frase_random(): 

    frases = [' Apuntá tus gastos fijos.','ahorra al menos el 10%.','Atende en la diferencia entre necesidad y deseo.','Compará precios.','Aprendé a invertir.']
    # frases_enlhet = ['epquen lhep apquelmaylha','enengqueneclha atquetsec 10','elano ac temaclha alpalhquem malhca ayaymommalhca tan apqueltamoc lha','elano lha cavam','eltamsap ac temaclha nenyausayc lha']
    
    return random.choice(frases)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefono = request.form['telefono']
        password = request.form['password']

        print('Login con los datos', telefono, password)

        try:
            usuario = Users.query.filter_by(telefono=telefono).first()
        except:
            usuario = None

        if usuario != None:
            dict_user = usuario.__dict__
            nombre = dict_user['nombre']
            pass_correcta = dict_user['password']
            # print(pass_correcta)
            if pass_correcta == password:
                print('Password correcta, Bienvenid@')
                return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono), frase=frase_random()))
            else:
                print('La pasword es incorrecta. ')

    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        password = request.form['password']
        confirma = request.form['confirmacion']
        print("Nuevo usuario con estos datos", nombre, telefono, password, confirma)

        try:
            usuario_existente = db.session.execute(
                db.select(Users).filter_by(telefono=telefono)).one()
        except:
            usuario_existente = None

        if usuario_existente == None:
            if password == confirma:
                usuario = Users(nombre, telefono, password)
                db.session.add(usuario)
                db.session.commit()
                return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono), frase=frase_random()))
        else:
            print('Ya existe un dato con ese usuario ')

    return render_template('sign_up.html')

@app.route("/ingresar_datos", methods=['GET', 'POST'])
def ingresar_datos():
    if request.method == 'POST':
        # Verificamos los argumentos recibidos de la pagina de sign_up o login
        args = request.args
        try:
            nombre = args['nombre']
            telefono = args['telefono']
        except:
            # Si intenta ingresar a la pagina principal sin iniciar sesion, le redireccionamos
            print('No iniciaste sesion, master. ')
            return redirect(url_for('login'))

        # Validamos que los datos de ingreso y egreso se procesen solo si ya se inicio sesion
        opcion = request.form['opcion']
        monto = request.form['monto']
        categoria = request.form['categoria']

        print('Se recibio la transaccion de', opcion, monto, categoria, telefono)

        # Realizamos las operaciones necesarias segun sea ingreso o egreso
        if (opcion == 'ingreso') and (categoria in categorias_validas_ingreso):
            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
            return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono), frase=frase_random()))
        elif (opcion == 'egreso') and (categoria in categorias_validas_egreso):
            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
            return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono), frase=frase_random()))
        else:
            print('La transaccion no corresponde con la categoria. ')

    return render_template('ingresar_datos.html')

@app.route('/pagina_principal')
def pagina_principal():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    print('Los argumentos de la pagina son', nombre, telefono)
    print('El saldo es ', calcular_saldo(telefono))

    generar_grafico(telefono) # Generamos el grafico de egresos

    return render_template('pagina_principal.html', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono), frase=frase_random())

@app.route("/")
def index():
    return render_template('inicio.html')

@app.route("/balance/<telefono>")
def balance(telefono):

    transacciones =  db.session.query(Transactions).filter_by(telefono=telefono).all()
    lista_de_transacciones = [] 
    saldo = 0

    for transaccion in transacciones:
        transaccion = transaccion.__dict__

        if transaccion['transaccion'] == 'ingreso':
            saldo += transaccion['monto']
            lista_de_transacciones.append([transaccion['monto'], '', saldo, 'Hubo un ingreso :)'])
        else: 
            saldo -= transaccion['monto']
            lista_de_transacciones.append(['', transaccion['monto'], saldo, 'Hubo un egreso ;(']) 
    print(generar_porcentajes(telefono))
    return render_template('balance.html', telefono=telefono, lista_de_transacciones=lista_de_transacciones)  

@app.route("/aprender")
def aprender():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
        saldo = args['saldo']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    return render_template('aprender.html', nombre=nombre, telefono=telefono, saldo=saldo)

@app.route("/inicio")
def inicio():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
        saldo = args['saldo']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    return render_template('inicio.html', nombre=nombre, telefono=telefono, saldo=saldo)

@app.route("/quienes_somos")
def quienes_somos():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
        saldo = args['saldo']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    return render_template('quienes_somos.html', nombre=nombre, telefono=telefono, saldo=saldo)

@app.route("/perfil")
def perfil():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
        saldo = args['saldo']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    return render_template('perfil.html', nombre=nombre, telefono=telefono, saldo=saldo)

@app.route("/galeria")
def galeria():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
        saldo = args['saldo']
    except:
        print('No iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    return render_template('galeria.html', nombre=nombre, telefono=telefono, saldo=saldo)

def generar_porcentajes(telefono): 
    egreso_total = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').scalar() 
    
    egreso_supermercado = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='supermercado').scalar() 

    egreso_movilidad = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='movilidad').scalar()

    egreso_entretenimiento = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='entretenimiento').scalar()

    egreso_vivienda = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='vivienda').scalar()

    egreso_deudas = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='deudas').scalar() 

    egreso_servicios = db.session.query(func.sum(Transactions.monto)).filter_by(telefono=telefono).filter_by(transaccion='egreso').filter_by(categoria='servicios').scalar() 

    lista_egresos = [egreso_vivienda, egreso_deudas, egreso_servicios, egreso_supermercado, egreso_movilidad, egreso_entretenimiento]

    porcentaje = []
    for egreso in lista_egresos: 
        if egreso != None: 
            porcentaje.append(egreso/egreso_total*100)
        else: 
            porcentaje.append(0)

    print (porcentaje)
    return porcentaje



# probando@dani-datos.iam.gserviceaccount.com
def generar_grafico(telefono):
    SERVICE_ACCOUNT_FILE = 'llave.json'
    credentials = service_account.Credentials.from_service_account_file(
        filename=SERVICE_ACCOUNT_FILE
    )

    service_sheets = build('sheets', 'v4', credentials=credentials)
    GOOGLE_SHEETS_ID = '1zsCw3bD6eg77UyJUR5A1c__y81_gnkcHIP73kadxteY'
    worksheet_name = 'tabla!'


    global cont
    cont = 2 

    def subir_a_sheets(categoria, porcentaje):
        global cont
        
        cell_range_insert = ('B' + str(cont) + ':' + 'C' + str(cont))

        cont = cont + 1
        
        values = (
            (categoria, porcentaje),
        )
        value_range_body = { 
            'majorDimension': 'ROWS',
            'values': values
        }

        service_sheets.spreadsheets().values().update(
            spreadsheetId=GOOGLE_SHEETS_ID,
            valueInputOption='USER_ENTERED',
            range=worksheet_name + cell_range_insert,
            body=value_range_body
        ).execute()

    porcentajes = generar_porcentajes(telefono) 
    for i in range(len(porcentajes)):
        subir_a_sheets(categorias_validas_egreso[i], porcentajes[i])

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True, port=8080)
