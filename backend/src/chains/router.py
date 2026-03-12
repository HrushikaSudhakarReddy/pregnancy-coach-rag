from typing import Dict, Any

def route_intent(text:str, profile:Dict[str,Any])->str:
    t=text.lower()
    if any(k in t for k in ['workout','exercise','gym','walk','strength','yoga']):
        return 'fitness'
    if any(k in t for k in ['meal','diet','eat','snack','recipe','food','nutrition']):
        return 'diet'
    if any(k in t for k in ['vitamin','supplement','prenatal','dha','iron','folate','folic']):
        return 'vitamins'
    return 'faq'
