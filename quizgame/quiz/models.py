from django.db import models
from django.contrib.postgres.fields import ArrayField

class Question(models.Model):
    text = models.CharField(max_length=255)
    options = models.JSONField()  # ["A", "B", "C", "D"]
    answer = models.IntegerField()  # indice corretto (0-3)

    def __str__(self):
        return self.text


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
