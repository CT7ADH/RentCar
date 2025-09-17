from flask import Flask

app = Flask(__name__)


from app.routers import home
