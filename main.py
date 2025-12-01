# -*- coding: utf-8 -*-
from app import app


if __name__ == "__main__":
    # Colocar o site no ar
    #app.run(debug=True)
    app.run(debug=True, host='0.0.0.0')


