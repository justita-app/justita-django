# Justita Project

## project setup



1- SetUp venv
```
virtualenv -p python3.11 venv
source venv/bin/activate
```

2- install Dependencies
```
pip install -r requirements.txt
```

3- create your env
```
cp .env.example .env
```

4- spin off docker compose
```
docker compose -f docker-compose.dev.yml up -d
```

5- Create tables
```
python manage.py migrate
```

6- run the project
```
python manage.py runserver 0.0.0.0:8000
```