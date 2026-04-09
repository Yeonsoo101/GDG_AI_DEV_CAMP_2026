import re
from typing import List
from google.adk.tools import ToolContext


# --- Content Analysis Tools ---

def count_words(text: str) -> int:
    """Counts the number of words in the provided text."""
    # TODO: #REPLACE-count-words
    # Split text on whitespace and return the count.
    print(f"🔧 Tool: Counting words...")
    pass  # Replace this line


def calculate_readability_score(text: str) -> dict:
    """Calculates a readability score (0-100, higher is easier to read)."""
    print(f"🔧 Tool: Calculating readability...")
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        return {"score": 0, "grade": "Unable to calculate"}

    words = text.split()
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(word) for word in words)

    if total_words == 0 or total_sentences == 0:
        score = 0
    else:
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        score = max(0, min(100, score))

    if score >= 60:
        grade = "Easy to read"
    elif score >= 50:
        grade = "Moderate"
    else:
        grade = "Complex"

    result = {"score": round(score, 2), "grade": grade}
    print(f"   Result: {result['score']} - {result['grade']}")
    return result


def count_syllables(word: str) -> int:
    """Helper function to estimate syllables in a word. PROVIDED — do not modify."""
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    if word.endswith('e'):
        syllable_count -= 1
    return max(1, syllable_count)


def generate_hashtags(text: str, count: int) -> List[str]:
    """Generates relevant hashtags from text by extracting key terms."""
    print(f"🔧 Tool: Generating {count} hashtags...")
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were',
        'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'of', 'to', 'for', 'in',
        'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'and',
        'or', 'but', 'if', 'then', 'than', 'so', 'this', 'that', 'these', 'those'
    }

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, freq in sorted_words[:count]]
    hashtags = [f"#{word.capitalize()}" for word in top_words]

    print(f"   Result: {', '.join(hashtags)}")
    return hashtags


# --- Quality Check Tool ---

def calculate_content_quality_score(
    word_count: int,
    readability_score: float,
    has_headings: bool,
    has_conclusion: bool
) -> dict:
    """Calculates overall content quality score based on multiple factors."""
    print(f"🔧 Tool: Calculating quality score...")
    if word_count < 500:
        word_score = 30
    elif word_count < 800:
        word_score = 60
    elif word_count <= 2000:
        word_score = 100
    else:
        word_score = 80

    read_score = min(100, readability_score * 1.5) if readability_score > 0 else 40

    structure_score = 0
    if has_headings:
        structure_score += 50
    if has_conclusion:
        structure_score += 50

    overall_score = (word_score * 0.3) + (read_score * 0.3) + (structure_score * 0.4)

    result = {
        "overall_score": round(overall_score, 2),
        "word_count": word_count,
        "meets_threshold": overall_score >= 70
    }
    print(f"   Result: {result['overall_score']}/100 (Threshold: {'MET' if result['meets_threshold'] else 'NOT MET'})")
    return result


# --- Loop Control ---

QUALITY_THRESHOLD_MET = "QUALITY_THRESHOLD_MET"


def exit_loop(tool_context: ToolContext):
    """Terminates the improvement loop when quality meets threshold."""
    print(f"🔧 Tool: Quality approved. Terminating loop...")
    tool_context.actions.escalate = True
    return {"result": "Quality threshold met. Content approved."}
