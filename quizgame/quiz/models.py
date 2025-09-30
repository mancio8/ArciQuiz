from django.db import models
from django.contrib.postgres.fields import ArrayField

from django.db import models

class Question(models.Model):
    TYPE_CHOICES = [
        ('quiz', 'Quiz classico'),
        ('anagram', 'Anagramma'),
        ('truefalse', 'Vero/Falso'),
    ]

    text = models.CharField(max_length=255)
    options = models.JSONField(blank=True, null=True)  # ["A","B","C","D"] oppure ["Vero","Falso"]
    answer = models.IntegerField()  # indice corretto
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='quiz')
    points = models.IntegerField(default=1)  # punti della domanda

    def __str__(self):
        return f"{self.text} ({self.get_type_display()})"



class GameState(models.Model):
    current_question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True
    )
    buzzed_queue = ArrayField(models.CharField(max_length=50), default=list, blank=True)

    # punteggi dei 4 team
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    score_team3 = models.IntegerField(default=0)
    score_team4 = models.IntegerField(default=0)

    def reset_buzz(self):
        self.buzzed_queue = []
        self.save()

    def next_player(self):
        """Passa al prossimo giocatore in coda"""
        if self.buzzed_queue:
            self.buzzed_queue.pop(0)
            self.save()
