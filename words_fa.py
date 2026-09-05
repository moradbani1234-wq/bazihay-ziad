"""لیست کلمات ۵ حرفی فارسی و منطق بازی حدس کلمه (شبیه Wordle)."""

_NORMALIZE_MAP = str.maketrans(
    {"ي": "ی", "ك": "ک", "أ": "ا", "إ": "ا", "ة": "ه", "ؤ": "و", "ئ": "ی"}
)


def normalize(word: str) -> str:
    return word.translate(_NORMALIZE_MAP).strip()


WORDS = [
    "مدرسه", "پرنده", "ماشین", "کبوتر", "دیوار", "باغچه", "گلدان",
    "نارنج", "کارگر", "پرستو", "گنجشک", "شکلات", "آسمان", "باران",
    "سرباز", "پرتاب", "گلابی", "انگور", "خرگوش", "ستاره", "پنجره",
    "گیلاس", "گاراژ", "سلامت", "پاییز", "شکوفه", "مهندس",
]


def evaluate_guess(guess: str, target: str) -> list[str]:
    """برای هر حرف یکی از سه حالت را برمی‌گرداند: correct / present / absent."""
    result = ["absent"] * len(guess)
    target_chars = list(target)

    for i, ch in enumerate(guess):
        if i < len(target) and ch == target[i]:
            result[i] = "correct"
            target_chars[i] = None

    for i, ch in enumerate(guess):
        if result[i] == "correct":
            continue
        if ch in target_chars:
            result[i] = "present"
            target_chars[target_chars.index(ch)] = None

    return result
