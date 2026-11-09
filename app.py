"""Quiz Engine

A small student quiz built with Streamlit and SQLite.

Run it with:
    streamlit run app.py
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).with_name("quiz.db")
QUIZ_SECONDS = 10 * 60
LETTERS = ("A", "B", "C", "D")

CATEGORIES = {
    "Python Basics": "Variables, functions, and simple Python.",
    "General Knowledge": "Places, people, and everyday facts.",
    "Science": "Nature, space, and how things work.",
}

# category, question, A, B, C, D, correct letter
QUESTIONS = [
    (
        "Python Basics",
        "What does print() do?",
        "It saves a file",
        "It shows text on the screen",
        "It deletes a variable",
        "It closes Python",
        "B",
    ),
    (
        "Python Basics",
        "Which symbol starts a comment in Python?",
        "Two slashes (//)",
        "A slash and a star (/*)",
        "A hash symbol (#)",
        "Two dashes (--)",
        "C",
    ),
    (
        "Python Basics",
        "What file extension does a Python file usually use?",
        ".py",
        ".java",
        ".exe",
        ".html",
        "A",
    ),
    (
        "Python Basics",
        "Which keyword defines a function?",
        "func",
        "def",
        "function",
        "define",
        "B",
    ),
    (
        "Python Basics",
        "What type of value does input() return?",
        "An integer",
        "A list",
        "A string",
        "A Boolean",
        "C",
    ),
    (
        "Python Basics",
        "Which value is a list?",
        "(1, 2, 3)",
        "{1, 2, 3}",
        "[1, 2, 3]",
        '{"a": 1}',
        "C",
    ),
    (
        "Python Basics",
        'What does len("cat") return?',
        "2",
        "3",
        "4",
        "cat",
        "B",
    ),
    (
        "Python Basics",
        "Which operator raises a number to a power?",
        "One asterisk",
        "Two asterisks",
        "A caret",
        "A percent sign",
        "B",
    ),
    (
        "Python Basics",
        "Which of these is a valid variable name?",
        "2score",
        "my-score",
        "class",
        "score_total",
        "D",
    ),
    (
        "Python Basics",
        "Which keyword starts a decision?",
        "if",
        "print",
        "def",
        "import",
        "A",
    ),
    (
        "General Knowledge",
        "What is the capital city of France?",
        "Lyon",
        "Paris",
        "Nice",
        "Rome",
        "B",
    ),
    (
        "General Knowledge",
        "Which is the largest ocean on Earth?",
        "Atlantic Ocean",
        "Indian Ocean",
        "Arctic Ocean",
        "Pacific Ocean",
        "D",
    ),
    (
        "General Knowledge",
        "How many continents are there?",
        "5",
        "6",
        "7",
        "8",
        "C",
    ),
    (
        "General Knowledge",
        "Which planet is closest to the Sun?",
        "Venus",
        "Mercury",
        "Mars",
        "Earth",
        "B",
    ),
    (
        "General Knowledge",
        "Who wrote Romeo and Juliet?",
        "Charles Dickens",
        "Mark Twain",
        "William Shakespeare",
        "Jane Austen",
        "C",
    ),
    (
        "General Knowledge",
        "What is the chemical symbol for water?",
        "O2",
        "CO2",
        "H2O",
        "NaCl",
        "C",
    ),
    (
        "General Knowledge",
        "How many days are in a leap year?",
        "365",
        "366",
        "364",
        "360",
        "B",
    ),
    (
        "General Knowledge",
        "What is the currency of Japan?",
        "Yuan",
        "Won",
        "Yen",
        "Dollar",
        "C",
    ),
    (
        "General Knowledge",
        "Which animal is the largest mammal?",
        "African elephant",
        "Blue whale",
        "Giraffe",
        "Polar bear",
        "B",
    ),
    (
        "General Knowledge",
        "Which set lists the primary colors of light?",
        "Red, yellow, and blue",
        "Red, green, and blue",
        "Blue, yellow, and white",
        "Orange, green, and purple",
        "B",
    ),
    (
        "Science",
        "Which gas do plants take in during photosynthesis?",
        "Oxygen",
        "Nitrogen",
        "Carbon dioxide",
        "Hydrogen",
        "C",
    ),
    (
        "Science",
        "What force pulls objects toward Earth?",
        "Magnetism",
        "Friction",
        "Gravity",
        "Electricity",
        "C",
    ),
    (
        "Science",
        "What is the boiling point of water at sea level, in Celsius?",
        "0",
        "50",
        "100",
        "90",
        "C",
    ),
    (
        "Science",
        "What is the center of an atom called?",
        "Nucleus",
        "Electron",
        "Molecule",
        "Cell",
        "A",
    ),
    (
        "Science",
        "Which organ pumps blood through the body?",
        "Lungs",
        "Stomach",
        "Heart",
        "Brain",
        "C",
    ),
    (
        "Science",
        "What process do plants use to make food?",
        "Digestion",
        "Photosynthesis",
        "Evaporation",
        "Freezing",
        "B",
    ),
    (
        "Science",
        "Which state of matter has a fixed shape and a fixed volume?",
        "Gas",
        "Liquid",
        "Plasma",
        "Solid",
        "D",
    ),
    (
        "Science",
        "Which planet is known as the Red Planet?",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "B",
    ),
    (
        "Science",
        "What is the unit of electric current?",
        "Volt",
        "Watt",
        "Ohm",
        "Ampere",
        "D",
    ),
    (
        "Science",
        "What do we call animals that eat only plants?",
        "Carnivores",
        "Omnivores",
        "Herbivores",
        "Predators",
        "C",
    ),
]


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the tables and load the 30 questions once."""
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                category TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage INTEGER NOT NULL,
                seconds_used INTEGER NOT NULL,
                taken_at TEXT NOT NULL
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO questions (
                    category, question, option_a, option_b, option_c, option_d, correct_option
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                QUESTIONS,
            )


def load_questions(category):
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM questions WHERE category = ? ORDER BY id",
            (category,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_attempt(name, category, score, total, percentage, seconds_used):
    taken_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO attempts (
                student_name, category, score, total, percentage, seconds_used, taken_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, score, total, percentage, seconds_used, taken_at),
        )


def recent_attempts(name):
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT category, score, total, percentage, taken_at
            FROM attempts
            WHERE student_name = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (name,),
        ).fetchall()
    return rows


def choice_text(question, letter):
    columns = {
        "A": "option_a",
        "B": "option_b",
        "C": "option_c",
        "D": "option_d",
    }
    if letter not in columns:
        return "Not answered"
    return f"{letter}. {question[columns[letter]]}"


def init_state():
    if "step" not in st.session_state:
        st.session_state.step = "name"
        st.session_state.student_name = ""


def clear_answers():
    """Clear both persistent answers and the temporary radio widget values."""
    st.session_state.answers = {}
    for key in list(st.session_state.keys()):
        if key.startswith("answer_"):
            del st.session_state[key]


def save_answer(question_id):
    """Copy a radio-button value into storage that survives page changes."""
    widget_key = f"answer_{question_id}"
    picked = st.session_state.get(widget_key)
    if picked is not None:
        st.session_state.answers[question_id] = picked


def start_quiz(category):
    questions = load_questions(category)
    clear_answers()
    st.session_state.category = category
    st.session_state.questions = questions
    st.session_state.index = 0
    st.session_state.started = time.time()
    st.session_state.deadline = time.time() + QUIZ_SECONDS
    st.session_state.done = False
    st.session_state.timed_out = False
    st.session_state.step = "quiz"


def finish_quiz(timed_out):
    """Score the quiz once and save the result."""
    if st.session_state.get("done"):
        st.session_state.step = "result"
        return

    questions = st.session_state.questions
    review = []
    score = 0
    for number, question in enumerate(questions, start=1):
        picked = st.session_state.get("answers", {}).get(question["id"])
        correct = picked == question["correct_option"]
        if correct:
            score += 1
        review.append(
            {
                "number": number,
                "question": question["question"],
                "yours": choice_text(question, picked),
                "correct": choice_text(question, question["correct_option"]),
                "is_correct": correct,
            }
        )

    total = len(questions)
    percentage = round(score * 100 / total) if total else 0
    seconds_used = int(time.time() - st.session_state.started)
    seconds_used = max(0, min(QUIZ_SECONDS, seconds_used))
    save_attempt(
        st.session_state.student_name,
        st.session_state.category,
        score,
        total,
        percentage,
        seconds_used,
    )
    st.session_state.score = score
    st.session_state.total = total
    st.session_state.percentage = percentage
    st.session_state.seconds_used = seconds_used
    st.session_state.review = review
    st.session_state.timed_out = timed_out
    st.session_state.done = True
    st.session_state.step = "result"


def restart():
    clear_answers()
    for key in ("category", "questions", "index", "started", "deadline", "done", "timed_out", "review"):
        st.session_state.pop(key, None)
    st.session_state.student_name = ""
    st.session_state.step = "name"


def clock_text(seconds):
    minutes, secs = divmod(max(0, int(seconds)), 60)
    return f"{minutes:02d}:{secs:02d}"


@st.fragment(run_every=1)
def show_timer():
    remaining = int(st.session_state.deadline - time.time())
    if remaining <= 0:
        st.session_state.timed_out = True
        st.rerun(scope="app")
    st.metric("Time left", clock_text(remaining))


def page_name():
    st.title("Quiz Engine")
    st.write("Enter your name, pick a category, and answer 10 multiple-choice questions.")
    with st.form("name_form"):
        name = st.text_input("Student name", placeholder="For example, Alex")
        ready = st.form_submit_button("Continue", type="primary")
    if ready:
        clean_name = " ".join(name.split())
        if not clean_name:
            st.warning("Please enter your name.")
        else:
            st.session_state.student_name = clean_name
            st.session_state.step = "category"
            st.rerun()


def page_category():
    st.title("Choose a category")
    st.write(f"Hello, {st.session_state.student_name}. Each quiz has 10 questions and 10 minutes.")
    for name, summary in CATEGORIES.items():
        with st.container(border=True):
            st.subheader(name)
            st.write(summary)
            if st.button("Start quiz", key=f"start_{name}", type="primary"):
                start_quiz(name)
                st.rerun()
    if st.button("Use a different name"):
        restart()
        st.rerun()


def page_quiz():
    if time.time() >= st.session_state.deadline or st.session_state.get("timed_out"):
        finish_quiz(True)
        st.rerun()

    questions = st.session_state.questions
    index = st.session_state.index
    question = questions[index]

    left, right = st.columns([3, 1])
    with left:
        st.subheader(st.session_state.category)
        st.caption(f"{st.session_state.student_name} · Question {index + 1} of {len(questions)}")
    with right:
        show_timer()

    st.progress((index + 1) / len(questions))
    st.markdown(f"### {question['question']}")
    question_id = question["id"]
    widget_key = f"answer_{question_id}"

    # Streamlit may discard a widget's state when that question is not visible.
    # Restore its previous selection from the persistent answers dictionary.
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.get("answers", {}).get(question_id)

    st.radio(
        "Choose one answer",
        LETTERS,
        format_func=lambda letter: choice_text(question, letter),
        index=None,
        key=widget_key,
        on_change=save_answer,
        args=(question_id,),
    )
    st.caption("A blank answer is marked incorrect.")

    back, next_col, submit_col = st.columns(3)
    with back:
        if st.button("Back", disabled=index == 0, width="stretch"):
            st.session_state.index -= 1
            st.rerun()
    with next_col:
        if index < len(questions) - 1 and st.button("Next", type="primary", width="stretch"):
            st.session_state.index += 1
            st.rerun()
    with submit_col:
        if st.button("Submit quiz", width="stretch"):
            finish_quiz(False)
            st.rerun()


def result_message(percentage):
    if percentage == 100:
        return "Perfect score."
    if percentage >= 80:
        return "Great job."
    if percentage >= 50:
        return "Nice effort. Look through the review, then try again."
    return "Keep practicing. The review below shows each correct answer."


def page_result():
    name = st.session_state.student_name
    score = st.session_state.score
    total = st.session_state.total
    percentage = st.session_state.percentage

    st.title("Your result")
    st.metric("Score", f"{percentage}%", f"{score} out of {total}")
    st.write(f"{name}, {result_message(percentage)}")
    st.write(f"Category: {st.session_state.category}")
    st.write(f"Time used: {clock_text(st.session_state.seconds_used)}")
    if st.session_state.timed_out:
        st.warning("Time is up. The quiz was submitted automatically.")

    if st.button("Restart", type="primary"):
        restart()
        st.rerun()

    st.subheader("Answer review")
    for item in st.session_state.review:
        status = "Correct" if item["is_correct"] else "Incorrect"
        with st.container(border=True):
            st.write(f"**{item['number']}. {item['question']}**")
            st.write(status)
            st.write(f"Your answer: {item['yours']}")
            st.write(f"Correct answer: {item['correct']}")

    st.subheader("Recent scores")
    attempts = recent_attempts(name)
    if not attempts:
        st.write("No saved scores yet.")
    for attempt in attempts:
        st.write(
            f"{attempt['taken_at']} — {attempt['category']}: "
            f"{attempt['score']}/{attempt['total']} ({attempt['percentage']}%)"
        )


def main():
    st.set_page_config(page_title="Quiz Engine", page_icon="📝", layout="centered")
    init_db()
    init_state()

    step = st.session_state.step
    if step == "name":
        page_name()
    elif step == "category":
        page_category()
    elif step == "quiz":
        page_quiz()
    else:
        page_result()


if __name__ == "__main__":
    main()
