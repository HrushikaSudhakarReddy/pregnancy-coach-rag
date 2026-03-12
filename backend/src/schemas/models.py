from pydantic import BaseModel
from typing import List, Optional
class UserProfile(BaseModel):
    weeks_pregnant: Optional[int]=None
    trimester: Optional[int]=None
    activity_level: Optional[str]=None
    dietary_pref: Optional[str]=None
    allergies: Optional[List[str]]=[]
    restrictions: Optional[List[str]]=[]
    conditions: Optional[List[str]]=[]
    dislikes: Optional[List[str]]=[]
    likes: Optional[List[str]]=[]
class ChatRequest(BaseModel):
    user_id:str
    message:str
    profile:UserProfile
class ChatResponse(BaseModel):
    intent:str
    reply:str
    citations:List[str]
    profile:UserProfile
    memory_summary: Optional[str]=None
