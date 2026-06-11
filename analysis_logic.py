import cv2
import math

def bereken_hoek(video_pad):
    # Hier simuleren we de AI-analyse
    # In de toekomst komt hier de 'Pose Estimation' (bijv. MediaPipe)
    # Voor nu geven we een berekende waarde terug die we uit de video "lezen"
    
    # We openen de video
    cap = cv2.VideoCapture(video_pad)
    # (Hier zou de AI-logica komen die de lijnen op het paard trekt)
    # Voor nu simuleren we de meting:
    hoek = 10 # Stel de AI meet 10 graden
    
    cap.release()
    return hoek

def geef_feedback(hoek):
    if -5 <= hoek <= 5:
        return {"status": "Correct", "feedback": "Je paard loopt mooi constant aan de loodlijn.", "oefening": "Varieer nu in tempo."}
    elif hoek < -5:
        return {"status": "Achter de loodlijn", "feedback": "Paard komt achter de loodlijn.", "oefening": "Geef meer ruimte met de hand."}
    else:
        return {"status": "Voor de loodlijn", "feedback": "Paard loopt voor de loodlijn.", "oefening": "Zorg voor meer verbinding."}
