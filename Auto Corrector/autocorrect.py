import streamlit as st
import nltk
import re
import string
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (only first run)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('punkt', quiet=True)

st.set_page_config(page_title="AutoCorrect App", layout="centered")

st.title("🔤 AutoCorrect System using NLP")
st.write("Upload a text dataset and get word correction suggestions.")

# ---------- Functions ----------
def count_word_frequency(words):
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def calculate_probability(word_count):
    total_words = sum(word_count.values())
    return {word: count / total_words for word, count in word_count.items()}

lemmatizer = WordNetLemmatizer()

def delete_letter(word):
    return [word[:i] + word[i+1:] for i in range(len(word))]

def swap_letters(word):
    return [word[:i] + word[i+1] + word[i] + word[i+2:] for i in range(len(word)-1)]

def replace_letter(word):
    letters = string.ascii_lowercase
    return [word[:i] + l + word[i+1:] for i in range(len(word)) for l in letters]

def insert_letter(word):
    letters = string.ascii_lowercase
    return [word[:i] + l + word[i:] for i in range(len(word)+1) for l in letters]

def generate_candidates(word):
    candidates = set()
    candidates.update(delete_letter(word))
    candidates.update(swap_letters(word))
    candidates.update(replace_letter(word))
    candidates.update(insert_letter(word))
    return candidates

def generate_candidates_level2(word):
    level1 = generate_candidates(word)
    level2 = set()
    for w in level1:
        level2.update(generate_candidates(w))
    return level2

def get_best_correction(word, probs, vocab, max_suggestions=3):
    candidates = (
        [word] if word in vocab else
        list(generate_candidates(word).intersection(vocab)) or
        list(generate_candidates_level2(word).intersection(vocab))
    )
    return sorted(
        [(w, probs.get(w, 0)) for w in candidates],
        key=lambda x: x[1],
        reverse=True
    )[:max_suggestions]

# ---------- Upload Dataset ----------
uploaded_file = st.file_uploader("📄 Upload text dataset (.txt)", type=["txt"])

if uploaded_file:
    text_data = uploaded_file.read().decode("utf-8").lower()
    words = re.findall(r'\w+', text_data)

    vocab = set(words)
    word_count = count_word_frequency(words)
    probabilities = calculate_probability(word_count)

    st.success("Dataset loaded successfully!")

    # ---------- User Input ----------
    user_word = st.text_input("✏️ Enter a word for autocorrection")

    if user_word:
        suggestions = get_best_correction(
            user_word.lower(),
            probabilities,
            vocab,
            max_suggestions=3
        )

        st.subheader("✅ Top Suggestions")
        if suggestions:
            for word, prob in suggestions:
                st.write(f"**{word}** — Probability: `{prob:.4f}`")
        else:
            st.warning("No suggestions found.")
else:
    st.info("Please upload a text dataset to continue.")
