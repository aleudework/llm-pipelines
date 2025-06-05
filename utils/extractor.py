import re

def clean_word(word):
    """
    Fjerner alle specialtegn fra ordet og laver det til små bogstaver.
    Beholder danske bogstaver (æ, ø, å).
    Eksempel: '**Materialeindkøb**' -> 'materialeindkøb'
    """
    return re.sub(r'[^\wæøåÆØÅ]', '', word, flags=re.UNICODE).lower()

def extract_label_from_response(response, labels=None, remove_thinking=True):
    """
    Finder det label (fx 'materialeindkøb' eller 'tjenesteydelse') som findes i svaret (response).
    Giver et præcist match, selv hvis svaret indeholder specialtegn eller store bogstaver.
    
    Parametre:
    - response: Svar fra modellen (skal helst være tekst/string)
    - labels: Liste med mulige labels (fx ['materialeindkøb', 'tjenesteydelse'])
    - remove_thinking: Hvis True fjernes tekst mellem <think>...</think>

    Returnerer:
    - match: Selve label-teksten fra labels-listen, hvis der er match. Ellers None.
    - response: Svaret uden <think>-sektion, hvis remove_thinking=True.
    - count_words: Ordbog med antal ord og antal ord inde i <think>.
    """

    match = None  # Her gemmes label hvis der findes et match

    # Opdel svaret i ord (inklusive evt. <think>-afsnit)
    words = response.split()
    # Fjern <think>...</think> og opdel igen
    words_without_think = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).split()

    # Tæl hvor mange ord der er i og uden for <think>
    count_words = {
        'thinking words': len(words) - len(words_without_think),  # ord i <think>
        'total words': len(words)                                 # alle ord i alt
    }

    # Hvis vi vil fjerne <think>-afsnittet, gør vi det nu
    if remove_thinking:
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        words = response.split()

    # Hvis der er labels at sammenligne med
    if labels:
        # Lav en renset version af labels (uden specialtegn, små bogstaver)
        labels_cleaned = [clean_word(label) for label in labels]
        # For hvert ord i svaret
        for word in words:
            word_cleaned = clean_word(word)
            # Sammenlign med alle rensede labels
            for label, label_cleaned in zip(labels, labels_cleaned):
                if word_cleaned == label_cleaned:
                    match = label   # Her returneres selve label-strengen, fx 'materialeindkøb'
                    break
            if match:
                break  # Stop hvis der allerede er fundet et match

    # Returnér label, evt. redigeret response, og ordoptælling
    return match, response, count_words