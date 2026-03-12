from typing import List
from collections import defaultdict
class Memory:
    def __init__(self): self.facts=defaultdict(list); self.summaries=defaultdict(str)
    def update(self,user_id:str,user_text:str,facts_to_remember:List[str]):
        for f in facts_to_remember:
            if f not in self.facts[user_id]: self.facts[user_id].append(f)
        if self.facts[user_id]: self.summaries[user_id]='; '.join(self.facts[user_id])[:300]
    def get_summary(self,user_id:str)->str: return self.summaries.get(user_id,'')
