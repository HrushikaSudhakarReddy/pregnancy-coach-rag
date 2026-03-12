# backend/app.py
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_DEBUG
from src.chains.answer import compose_answer
from src.chains.router import route_intent as route_intent_rules
from src.memory.state import Memory
from src.rag.retriever import get_retriever
from src.safety.red_flags import RED_FLAG_RESPONSE, has_red_flags
from src.schemas.models import ChatRequest, ChatResponse

logger = logging.getLogger("pregnancy-coach")
logger.setLevel(logging.INFO)

# ----------------------------
# Optional ML intent classifier
# ----------------------------
INTENT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "intent_classifier.joblib",
)
INTENT_CONF_THRESHOLD = 0.40

intent_clf = None
try:
    from src.nlp.intent_infer import IntentClassifier

    if os.path.exists(INTENT_MODEL_PATH):
        intent_clf = IntentClassifier(INTENT_MODEL_PATH)
        logger.info(f"[IntentClassifier] Loaded: {INTENT_MODEL_PATH}")
    else:
        logger.warning(
            f"[IntentClassifier] Model not found at {INTENT_MODEL_PATH}. Using rule-based router only."
        )
except Exception as e:
    logger.warning(
        f"[IntentClassifier] Could not initialize classifier: {e}. Using rule-based router only."
    )
    intent_clf = None

# -----------------------------
# Optional ML safety classifier
# -----------------------------
SAFETY_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "safety_classifier.joblib",
)
SAFETY_THRESH = 0.85

safety_clf = None
try:
    from src.nlp.safety_infer import SafetyClassifier

    if os.path.exists(SAFETY_MODEL_PATH):
        safety_clf = SafetyClassifier(SAFETY_MODEL_PATH)
        logger.info(f"[SafetyClassifier] Loaded: {SAFETY_MODEL_PATH}")
    else:
        logger.warning(f"[SafetyClassifier] Model not found at {SAFETY_MODEL_PATH}.")
except Exception as e:
    logger.warning(f"[SafetyClassifier] Could not initialize classifier: {e}.")
    safety_clf = None

app = FastAPI(title="Pregnancy Coach Bot (Ollama + Chroma)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = Memory()
retriever = get_retriever()

BENIGN_WELLNESS_KEYWORDS = [
    "workout",
    "exercise",
    "exercises",
    "meal",
    "meals",
    "food",
    "diet",
    "hydration",
    "water",
    "vitamin",
    "vitamins",
    "stretch",
    "stretches",
    "yoga",
    "mobility",
    "strength",
    "routine",
    "plan",
    "fitness",
    "snack",
    "snacks",
    "protein",
    "walking",
    "walk",
]

MEDICAL_RISK_HINTS = [
    "pain",
    "bleeding",
    "spotting",
    "dizziness",
    "fainting",
    "fever",
    "contractions",
    "cramping",
    "headache",
    "swelling",
    "vision",
    "shortness of breath",
    "chest pain",
    "discharge",
    "vomiting",
    "nausea",
    "reduced fetal movement",
    "decreased fetal movement",
    "baby not moving",
]


def to_profile_dict(profile):
    """Handle pydantic .dict() vs plain dict transparently."""
    if hasattr(profile, "dict"):
        return profile.dict()
    try:
        return dict(profile)
    except Exception:
        return {}


def is_clearly_benign_wellness_query(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in BENIGN_WELLNESS_KEYWORDS)


def looks_medical_or_risky(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in MEDICAL_RISK_HINTS)


def infer_intent(text: str, profile_dict: dict) -> tuple[str, float, str]:
    """
    Returns (final_intent, confidence, source)
    source ∈ {"ml", "rules", "ml_fallback_rules"}
    """
    if has_red_flags(text):
        return "safety", 1.0, "rules"

    if intent_clf is not None:
        try:
            label, conf = intent_clf.predict(text, threshold=INTENT_CONF_THRESHOLD)
            if conf < INTENT_CONF_THRESHOLD:
                rules_label = route_intent_rules(text, profile_dict)
                logger.info(
                    f"[Router] ML low conf ({conf:.2f}) -> fallback rules intent={rules_label}"
                )
                return rules_label, conf, "ml_fallback_rules"

            logger.info(f"[Router] ML intent={label} conf={conf:.2f}")
            return label, conf, "ml"
        except Exception as e:
            logger.warning(f"[Router] ML routing failed ({e}); falling back to rules.")

    rules_label = route_intent_rules(text, profile_dict)
    logger.info(f"[Router] Rules intent={rules_label}")
    return rules_label, 1.0, "rules"


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    profile_dict = to_profile_dict(req.profile)

    # ----------------------------------------
    # Safety layer #1: explicit red-flag rules
    # ----------------------------------------
    if has_red_flags(text):
        return ChatResponse(
            intent="safety",
            reply=RED_FLAG_RESPONSE,
            citations=[],
            profile=req.profile,
            memory_summary=memory.get_summary(req.user_id),
        )

    # ---------------------------------------------------
    # Safety layer #2: ML safety gate for ambiguous cases
    # ---------------------------------------------------
    # Do NOT let ML block clearly safe wellness requests like:
    # "give me a workout", "meal plan", "hydration tips", etc.
    clearly_benign = is_clearly_benign_wellness_query(text)
    medically_ambiguous = looks_medical_or_risky(text)

    if safety_clf is not None and (not clearly_benign) and medically_ambiguous:
        try:
            s_label, s_conf = safety_clf.predict(text, thresh=SAFETY_THRESH)
            logger.info(f"[SafetyClassifier] label={s_label} conf={s_conf:.2f}")

            if s_label == "unsafe":
                return ChatResponse(
                    intent="safety",
                    reply=(
                        RED_FLAG_RESPONSE
                        + "\n\n*Note: flagged by ML safety gate; please consult your provider.*"
                    ),
                    citations=[],
                    profile=req.profile,
                    memory_summary=memory.get_summary(req.user_id),
                )
        except Exception as e:
            logger.warning(f"[SafetyClassifier] inference failed: {e}")

    # -------------------------
    # Intent routing
    # -------------------------
    intent, conf, source = infer_intent(text, profile_dict)
    logger.info(f"[Chat] final_intent={intent} conf={conf:.2f} source={source}")

    # -------------------------
    # Retrieve supporting docs
    # -------------------------
    docs = retriever(text, intent=intent, profile=profile_dict)

    # -------------------------
    # Compose final answer
    # -------------------------
    result = compose_answer(text, intent, docs, profile_dict) or {}
    reply_text = result.get("message", "")

    if intent == "safety":
        reply_text += (
            "\n\n*Note: This is not medical advice. Please consult your healthcare provider for guidance specific to you.*"
        )

    # -------------------------
    # Memory update
    # -------------------------
    memory.update(req.user_id, text, result.get("facts_to_remember", []))

    return ChatResponse(
        intent=intent,
        reply=reply_text,
        citations=result.get("citations", []),
        profile=req.profile,
        memory_summary=memory.get_summary(req.user_id),
    )


@app.get("/healthz")
def health():
    details = {"ok": True, "debug": APP_DEBUG}
    details["intent_router"] = "ml+rules" if intent_clf else "rules"
    details["safety_gate"] = "rules+ml" if safety_clf else "rules"
    details["safety_threshold"] = SAFETY_THRESH
    return details