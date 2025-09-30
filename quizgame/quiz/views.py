from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import GameState, Question
from django.views.decorators.csrf import csrf_exempt


def current_question(request):
    """Vista concorrenti: domanda + risposte + punteggi"""
    state = GameState.objects.first()
    question = state.current_question if state else None

    context = {
        "question": question,
        "scores": {
            "Team 1": state.score_team1 if state else 0,
            "Team 2": state.score_team2 if state else 0,
            "Team 3": state.score_team3 if state else 0,
            "Team 4": state.score_team4 if state else 0,
        } if state else {},
    }
    return render(request, "quiz/current_question.html", context)


def conductor_dashboard(request):
    """Dashboard conduttore: elenco domande, punteggi e prenotati"""
    state, _ = GameState.objects.get_or_create(id=1)
    questions = Question.objects.all()
    current_player = state.buzzed_queue[0] if state.buzzed_queue else None
    return render(request, "quiz/dashboard.html", {
        "state": state,
        "questions": questions,
        "current_player": current_player,
    })


def set_question(request, qid):
    """Imposta la domanda corrente"""
    state, _ = GameState.objects.get_or_create(id=1)
    question = get_object_or_404(Question, id=qid)
    state.current_question = question
    state.reset_buzz()
    state.save()
    return redirect("conductor_dashboard")

@csrf_exempt
def buzz(request):
    """ESP32 invia prenotazione → aggiunta in coda"""
    if request.method == "POST":
        player = request.POST.get("player")
        state = GameState.objects.first()
        if state:
            if player not in state.buzzed_queue:
                state.buzzed_queue.append(player)
                state.save()
                return JsonResponse({"status": "ok", "queue": state.buzzed_queue})
            return JsonResponse({"status": "already_in_queue"})
    return JsonResponse({"status": "error"})


def add_point(request, team):
    """Aggiunge 1 punto al team scelto"""
    state = GameState.objects.first()
    if not state:
        return redirect("conductor_dashboard")

    if team == 1:
        state.score_team1 += 1
    elif team == 2:
        state.score_team2 += 1
    elif team == 3:
        state.score_team3 += 1
    elif team == 4:
        state.score_team4 += 1

    state.save()
    state.reset_buzz()  # dopo risposta corretta si svuota la coda
    return redirect("conductor_dashboard")


def wrong_answer(request):
    """Il giocatore attuale ha sbagliato → passa al successivo"""
    state = GameState.objects.first()
    if state:
        state.next_player()
    return redirect("conductor_dashboard")

def reset_game(request):
    state, created = GameState.objects.get_or_create(id=1)
    
    # Ripristina punteggi
    state.score_team1 = 0
    state.score_team2 = 0
    state.score_team3 = 0
    state.score_team4 = 0

    # Svuota coda buzzers
    state.buzzed_queue = []

    # Imposta la prima domanda (se esiste)
    first_question = Question.objects.first()
    state.current_question = first_question

    state.save()

    return redirect('conductor_dashboard')


