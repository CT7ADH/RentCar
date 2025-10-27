from app import app, db
from flask import render_template, url_for, request, redirect, flash, session
from datetime import datetime
from app.models import Cliente, Veiculo
from functools import wraps

def login_required(f):
    """Decorator para rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route("/")
@app.route("/index")
def home():
    """ Página Inicial"""
    return render_template("index.html")

@app.route("/car-list")
def car_list():
    return render_template("car-list.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login de clientes"""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        cliente = Cliente.query.filter_by(email=email).first()

        if cliente and cliente.check_password(senha):
            session['user_id'] = cliente.id
            session['user_name'] = cliente.name
            flash(f'Bem-vindo, {cliente.name}!', 'success')

            # Redirecionar para a página solicitada ou home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Email ou senha inválidos.', 'danger')

    return render_template('login.html')

@app.route("/registration", methods=['GET', 'POST'])
def registration():
    """Registro de novos clientes"""
    if request.method == "POST":
         try:
             name = request.form["name"]
             email = request.form["email"]
             phone = request.form["phone"]
             birth_date = datetime.strptime(request.form["birth_date"], '%Y-%m-%d').date()
             password = request.form["password"]
             re_pass = request.form["re_pass"]

             # Validações
             if password != re_pass:
                 flash("Password não coincide!", 'danger')
                 return redirect(url_for('registration'))

             if Cliente.query.filter_by(email=email).first():
                 flash('Este email já está cadastrado.', 'danger')
                 return redirect(url_for('registration'))

             # Criar novo Cliente
             cliente = Cliente(
                 name = name.title(),
                 email = email.lower(),
                 phone = phone,
                 birth_date = birth_date,
             )
             cliente.set_password(password)

             db.session.add(cliente)
             db.session.commit()

             flash('Cliente registrado com sucesso!', 'success')
             return redirect(url_for('login'))
         except Exception as e:
             db.session.rollback()
             flash(str(e), 'danger')
    return render_template("registration.html")




@app.route("/reserva")
def reserva():
    return render_template("reserva.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

