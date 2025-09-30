
# Quiz Game Django + ESP32

## Descrizione
Quiz multiplayer gestito con Django e PostgreSQL.  
- Concorrenti possono prenotarsi per rispondere tramite ESP32 (o simulazione).  
- Conduttore gestisce le domande, assegna punti e passa al prossimo concorrente se sbaglia.  
- Le domande sono salvate in JSON/PostgreSQL.  

---

## Requisiti
- Python 3.11+
- Docker & Docker Compose
- pip
- Arduino IDE (opzionale per ESP32)
- requests (per simulare ESP)

---

## 1️⃣ Creazione progetto Django

```bash
django-admin startproject quizgame
cd quizgame
python manage.py startapp quiz
```

---

## 2️⃣ Configurazione PostgreSQL con Docker

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: quiz_postgres
    restart: always
    environment:
      POSTGRES_USER: quizuser
      POSTGRES_PASSWORD: quizpass
      POSTGRES_DB: quizdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    container_name: quiz_django
    command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_NAME=quizdb
      - DB_USER=quizuser
      - DB_PASSWORD=quizpass
      - DB_HOST=db
      - DB_PORT=5432

volumes:
  postgres_data:
```

`Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
```

`requirements.txt`:

```
Django>=4.2
psycopg2-binary
```

---

## 3️⃣ Configurazione Django per PostgreSQL

In `settings.py`:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'quizdb'),
        'USER': os.environ.get('DB_USER', 'quizuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'quizpass'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
INSTALLED_APPS += ['quiz', 'django.contrib.postgres']
```

---

## 4️⃣ Modelli (`quiz/models.py`)

```python
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Question(models.Model):
    text = models.CharField(max_length=255)
    options = models.JSONField()
    answer = models.IntegerField()

class GameState(models.Model):
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    buzzed_queue = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    score_team3 = models.IntegerField(default=0)
    score_team4 = models.IntegerField(default=0)

    def reset_buzz(self):
        self.buzzed_queue = []
        self.save()

    def next_player(self):
        if self.buzzed_queue:
            self.buzzed_queue.pop(0)
            self.save()
```

---

## 5️⃣ Views (`quiz/views.py`)

Include:
- `current_question` → vista concorrenti  
- `conductor_dashboard` → conduttore  
- `set_question` → imposta domanda  
- `buzz` → prenotazione ESP  
- `add_point` → aggiungi punto  
- `wrong_answer` → passa al prossimo  

*(vedi codice completo fornito precedentemente)*

---

## 6️⃣ URL (`quiz/urls.py`)

```python
from django.urls import path
from . import views

urlpatterns = [
    path("current/", views.current_question, name="current_question"),
    path("conductor/", views.conductor_dashboard, name="conductor_dashboard"),
    path("set/<int:qid>/", views.set_question, name="set_question"),
    path("buzz/", views.buzz, name="buzz"),
    path("add/<int:team>/", views.add_point, name="add_point"),
    path("wrong/", views.wrong_answer, name="wrong_answer"),
]
```

In `quizgame/urls.py`:

```python
path('quiz/', include('quiz.urls')),
```

---

## 7️⃣ Template

`quiz/templates/quiz/current_question.html` → concorrenti  
`quiz/templates/quiz/dashboard.html` → conduttore  

*(vedi codice completo fornito precedentemente)*

---

## 8️⃣ Migrazioni e superuser

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 9️⃣ Inserimento domande

### SQL diretto:

```sql
INSERT INTO quiz_question (text, options, answer) VALUES
('Qual è la capitale d''Italia?', '["Roma","Milano","Torino","Napoli"]', 0),
('Quale pianeta è conosciuto come Pianeta Rosso?', '["Venere","Marte","Giove","Saturno"]', 1);
```

### Simulazione Python/JSON:
Puoi creare un `load_questions.py` per importare da JSON.

---

## 🔟 Simulazione ESP32

### Python script:

```python
import requests
players = ["Team 1","Team 2","Team 3","Team 4"]
for p in players:
    r = requests.post("http://127.0.0.1:8000/quiz/buzz/", data={"player":p})
    print(p, r.json())
```

### Oppure con curl:

```bash
curl -X POST -d "player=Team 1" http://127.0.0.1:8000/quiz/buzz/
```

---

## 1️⃣1️⃣ Avvio completo con Docker

```bash
docker-compose up --build
```

- Django → http://localhost:8000/quiz/current/  
- Dashboard conduttore → http://localhost:8000/quiz/conductor/  
- PostgreSQL → porta 5432  


### Importa domande con json:

- Import → http://localhost:8000/quiz/import/


```json
[
  {
    "text": "IMPREVISTO! Rispondi velocissimo: 2+2=?",
    "options": ["Vero","Falso"],
    "answer": 1,
    "type": "truefalse",
    "points": 2
  },
  {
    "text": "In che provincia si trova Guardia Sanframondi?",
    "options": ["Benevento", "Avellino", "Caserta", "Salerno"],
    "answer": 0,
    "type": "quiz",
    "points": 2
  },
  {
    "text": "Ricostruisci la parola: G A R D I A",
    "options": ["GUARDIA"],
    "answer": 0,
    "type": "anagram",
    "points": 2
  }
]

```

