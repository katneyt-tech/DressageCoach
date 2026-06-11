def analyseer_loodlijn(hoek):
    # Dit is de logica: we meten de hoek van de neuslijn
    # Ideaal is rond de 0 graden (verticaal)
    
    if -5 <= hoek <= 5:
        return {
            "status": "Correct",
            "feedback": "Je paard loopt mooi aan de loodlijn. Je aanleuning lijkt stabiel.",
            "oefening": "Probeer dit gevoel vast te houden en varieer nu in tempo zonder dat de houding verandert."
        }
    elif hoek < -5:
        return {
            "status": "Achter de loodlijn",
            "feedback": "Je paard komt achter de loodlijn. Hij zoekt geen contact met je hand.",
            "oefening": "Rijd ruimere wendingen, geef meer ruimte met je hand en rijd actiever van achteruit naar voren."
        }
    else:
        return {
            "status": "Voor de loodlijn",
            "feedback": "Je paard loopt voor de loodlijn (tegen de hand in).",
            "oefening": "Zorg voor meer verbinding door je been en rijd meer overgangen om het paard op je hulpen te krijgen."
        }
