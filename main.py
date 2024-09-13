from flask import request, render_template, session, flash, redirect, url_for
from app import app
from models import db, Usuario, Receta, Ingrediente
from datetime import datetime
import hashlib

#Funciones
def validate_login(email, password):
    if not email or not password:
        return "Por favor ingrese los datos requeridos"
    
    usuario_actual = Usuario.query.filter_by(correo=email).first()
    
    if usuario_actual is None:
        return "El correo no está registrado"
    
    result = hashlib.md5(bytes(password, encoding='utf-8'))
    
    if result.hexdigest() != usuario_actual.clave:
        return "La contraseña no es válida"
    
    return None



##FLASK Rutas

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/bienvenido')
def bienvenido():
    return render_template('bienvenido.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        error = validate_login(email, password)
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('login'))
        
        usuario_actual = Usuario.query.filter_by(correo=email).first()
        session['usuario'] = usuario_actual.id
        return redirect(url_for('bienvenido'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not nombre or not email or not password or not confirm_password:
            flash('Por favor ingrese todos los datos requeridos', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))
        
        # Verificar si el correo ya está registrado
        usuario_existente = Usuario.query.filter_by(correo=email).first()
        if usuario_existente:
            flash('El correo ya está registrado', 'danger')
            return redirect(url_for('register'))
        
        # Crear un nuevo usuario
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        nuevo_usuario = Usuario(nombre=nombre, correo=email, clave=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/compartirreceta', methods=['GET', 'POST'])
def compartirreceta():
    if request.method == 'POST' or request.method == 'GET':
        return render_template('compartirreceta.html')

@app.route('/ingreso_receta', methods=['GET', 'POST'])
def ingreso_receta():
    if request.method == 'POST' or request.method == 'GET':
        if not request.form["nombre"] or not request.form["tiempo"] or not request.form["descripcion"] or not request.form["cing"]:
            return render_template('error.html', error="Por favor ingrese los datos requeridos")
        else:
            nueva_receta = Receta(nombre=request.form["nombre"], tiempo=request.form["tiempo"], fecha=datetime.now(), elaboracion=request.form["descripcion"], cantidadmegusta=0, usuarioid=session['usuario'])
            db.session.add(nueva_receta)
            db.session.commit()
            x = int(request.form["cing"])
            return render_template('ingresaringredientes.html', x=x, recetaid=nueva_receta.id)

@app.route('/ingresaringredientes', methods=['GET', 'POST'])
def ingresaringredientes():
    if request.method == 'POST' or request.method == 'GET':
        band = False
        x = (int(request.form["x"])) - 1
        c = 0
        while not band:
            nuevo_ingrediente = Ingrediente(nombre=request.form[f"nombrei{c}"], cantidad=request.form[f"cantidadi{c}"], unidad=request.form[f"unidad{c}"], recetaid=request.form["recetaid"])
            db.session.add(nuevo_ingrediente)
            db.session.commit()
            if c < x:
                c += 1
            elif c == x:
                band = True
        return render_template('ingredientescargados.html')

@app.route('/consultarranking', methods=['GET', 'POST'])
def consultarranking():
    if request.method == 'POST' or request.method == 'GET':
        listarecetas = Receta.query.order_by(Receta.cantidadmegusta.desc()).limit(5)
        return render_template('ranking.html', ordenada=listarecetas)

@app.route('/consultarreceta', methods=['GET', 'POST'])
def consultarreceta():
    return render_template('pidetiempo.html')

@app.route('/recetasportiempo', methods=['GET', 'POST'])
def recetasportiempo():
    if request.method == 'POST' or request.method == 'GET':
        tiempo = request.form["tiemporeceta"]
        listatiempomenor = Receta.query.filter(Receta.tiempo < tiempo)
        return render_template("muestrarecetas.html", lista=listatiempomenor)

@app.route('/listadorecetas', methods=['GET', 'POST'])
def listadorecetas():
    if request.method == 'POST':
        seleccionada = Receta.query.filter_by(id=request.form['recetaid']).first()
        listaing = []
        for Ingrediente in seleccionada.ingredientes:
            listaing.append(Ingrediente)
        user = Usuario.query.filter_by(id=seleccionada.usuarioid).first()
        return render_template('informacionreceta.html', Receta=seleccionada, lista=listaing, usuario=user)
    return redirect(url_for('ranking'))

@app.route('/megusta', methods=['GET', 'POST'])
def megusta():
    if request.method == 'POST' or request.method == 'GET':
        receta_actual = Receta.query.filter_by(id=request.form['recetaid']).first()
        receta_actual.cantidadmegusta += 1
        db.session.commit()
        return render_template("error.html", error="Me gusta registrado")

@app.route('/recetaporingrediente', methods=['GET', 'POST'])
def recetaporingrediente():
    if request.method == 'POST' or request.method == 'GET':
        return render_template('pideingrediente.html')

@app.route('/recetaporingredientedado', methods=['GET', 'POST'])
def recetaporingredientedado():
    tag = request.form["pideing"]
    listaing = Ingrediente.query.filter(Ingrediente.nombre.like('%' + tag + '%')).all()
    lista = []
    for i in range(len(listaing)):
        nueva_receta = Receta.query.filter_by(id=listaing[i].recetaid).first()
        lista.append(nueva_receta)
    return render_template('muestrarecetas.html', lista=lista)

if __name__ == '__main__':
    app.run(debug=True)