### commands:  
* criar/atualizar o requirements.txt
````
# you may need pip3 in linux
    pip freeze > requirements.txt
````
Criar um virtual enviroment(Windows):
````
    python -m venv .venv
    .venv\Scripts\activate
     pip install -r requirements.txt
````
Criar um virtual enviroment(Linux):
````
    python3 -m venv .venv
    ./.venv/bin/activate
    pip install -r requirements.txt
````
* Instala as dependências do requirements.txt
```
# you may need pip3 in linux
      pip install -r requirements.txt
```