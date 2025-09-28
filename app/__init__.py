from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Aumenta a produtividade do banco de dados, deixa de chequear ( em produção por em TRUE)
db = SQLAlchemy(app)
migrate = Migrate(app, db)



from app.routers import home
from app.models import Clientes, Veiculos, Reservas,FormasPagamento
#app.register_blueprint(home)
