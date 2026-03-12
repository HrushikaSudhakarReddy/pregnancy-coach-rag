import re
RED_FLAG_KEYWORDS=[r'vaginal bleeding',r'severe headache',r'vision changes',r'reduced fetal movement',r'chest pain',r'contractions.*before\s*37',r'preeclampsia',r'fainting',r'fever\s*(?:over|>|\babove\b)\s*38',r'severe abdominal pain']

def has_red_flags(text:str)->bool:
    t=text.lower()
    for pat in RED_FLAG_KEYWORDS:
        if re.search(pat,t):
            return True
    return False

RED_FLAG_RESPONSE=('I am concerned about symptoms you mentioned. For your safety, please contact your obstetric provider or seek urgent care immediately. I can share general information but I cannot provide medical advice.')
