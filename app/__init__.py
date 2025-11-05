from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Agua#Cafe_taladro!escovA?Velha'
#app.config['SECRET_KEY'] = 'c090032b65a7e1f79ae5b96ec79763b9b46342484c1537014be7f748ba4bbe8abe762b20ff7a1fa2e7e899fe29ded2a866a5f77846ff01bd0a2166003ef1e949'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Aumenta a produtividade do banco de dados, deixa de chequear ( em produção por em TRUE)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)



# Importa-se sempre no final do ficheiro
from app import routes
from app.models import Cliente, Veiculo, Reserva, FormasPagamento
#app.register_blueprint(home)
