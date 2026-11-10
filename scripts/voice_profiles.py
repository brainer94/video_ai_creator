import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEMINI_VOICE_PROFILE_DIR = ROOT / "gemini_voice_profile"
DEFAULT_PROJECT_VOICE_CONFIG = {
    "voice_provider": "gemini",
}
DEFAULT_SCENE_VOICE_KEY = "lily"
SCENE_VOICE_OPTIONS = [
    ("Lily (anak perempuan kalem)", "lily"),
    ("Lily - Ngaji", "lily_ngaji"),
    ("Lily - Arab", "lily_arab"),
]
VOICE_CHARACTER_MAP = {
    "lily": {
        "display_name": "Lily",
        "profile_file": "Lily.txt",
        "gemini_profile_text": "7 years old Indonesian youthful female voice with a soft and cute tone. Perfect for animated characters and storytelling. Ideal for bringing warmth and sweetness to playful or gentle characters.",
    },
    "lily_ngaji": {
        "display_name": "Lily - Ngaji",
        "profile_file": "Lily Ngaji.txt",
        "gemini_profile_text": "Soft, clear, youthful female Quran reciter with a gentle and beautiful tone. Use standardized, accurate Arabic pronunciation: preserve every harakah, makhraj, sifat, shaddah, sukun, hamzah, tanwin, grammatical ending, and short or long vowel (madd) exactly. Apply tajwid and natural waqaf correctly. Never shorten madd, lengthen short vowels, omit or merge consonants, guess unclear text, or silently alter the supplied Arabic. Melodious Quranic tilawah with a gentle murattal style and light Maqam Bayati-inspired contour, without instruments, background music, harmony, chorus, echo, or sound effects. Recite exactly the Arabic text provided.",
    },
    "lily_arab": {
        "display_name": "Lily - Arab",
        "profile_file": "Lily Arab.txt",
        "gemini_profile_text": "Soft, clear, youthful female Arabic reciter with a brisk flowing delivery that remains melodic, beautiful, peaceful, and easy to understand. Use standardized, accurate Arabic pronunciation: preserve every harakah, makhraj, sifat, shaddah, sukun, hamzah, tanwin, grammatical ending, and short or long vowel (madd) exactly. Apply tajwid and natural waqaf correctly. Never shorten madd, lengthen short vowels, omit or merge consonants, guess unclear text, or silently alter the supplied Arabic. Keep consonants intelligible, with no dragging or blurring. Recite exactly the Arabic text provided, without instruments, background music, harmony, chorus, echo, or sound effects.",
    },
}


def normalize_voice_key(value: str) -> str:
    key = str(value or "").strip().lower()
    if key in VOICE_CHARACTER_MAP:
        return key
    return DEFAULT_SCENE_VOICE_KEY


def resolve_scene_voice_key(scene_meta: dict) -> str:
    if not isinstance(scene_meta, dict):
        return DEFAULT_SCENE_VOICE_KEY
    raw = str(scene_meta.get("voice_character", "")).strip().lower()
    if raw in VOICE_CHARACTER_MAP:
        return raw
    return DEFAULT_SCENE_VOICE_KEY


def get_voice_character(voice_key: str) -> dict:
    key = normalize_voice_key(voice_key)
    voice = copy.deepcopy(VOICE_CHARACTER_MAP[key])
    profile_file = str(voice.get("profile_file", "")).strip()
    if profile_file:
        profile_path = GEMINI_VOICE_PROFILE_DIR / profile_file
        try:
            if profile_path.exists():
                profile_text = profile_path.read_text(encoding="utf-8").strip()
                if profile_text:
                    voice["gemini_profile_text"] = profile_text
        except OSError:
            pass
    return voice
