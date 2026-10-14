"""Console quiz grader: scores students, assigns grades and reports stats."""

import os
import re
import secrets
import shutil
# subprocess is used only with a fixed argv list and no shell.
import subprocess  # nosec B404

QUESTIONS = [
    {"q": "What is 2 + 2?", "answer": "4"},
    {"q": "Which keyword defines a function in Python?", "answer": "def"},
    {"q": "What does CPU stand for?", "answer": "Central Processing Unit"},
    {"q": "Which type is immutable: list or tuple?", "answer": "tuple"},
]
# Read the secret from the environment instead of hardcoding it.
PROCTOR_PASSWORD = os.environ.get("PROCTOR_PASSWORD", "")
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")
results = {}


def normalize_answer(text):
    """Return a case- and whitespace-insensitive form of an answer."""
    return text.strip().lower()


def pick_bonus_question():
    """Return the text of a randomly chosen question."""
    return secrets.choice(QUESTIONS)["q"]


def grade_student(student_name, responses, penalties=None):
    """Score a student's responses, record the result and return the score.

    If a penalties dict is passed, wrong answers are counted into it.
    """
    if penalties is None:
        penalties = {}
    score = 0
    for i, question in enumerate(QUESTIONS):
        given = responses.get(i, "")
        if normalize_answer(given) == normalize_answer(question["answer"]):
            score += 1
        else:
            penalties[student_name] = penalties.get(student_name, 0) + 1
    results[student_name] = score
    return score


def get_grade(score):
    """Map a raw score to a letter grade."""
    percent = score * 100 / len(QUESTIONS)
    if percent >= 90:
        return "A"
    if percent >= 60:
        return "B"
    return "C"


def class_average():
    """Return the mean score rounded to 2 decimals (0 if no results)."""
    if not results:
        return 0
    return round(sum(results.values()) / len(results), 2)


def topper():
    """Return the highest-scoring student, or None if no results."""
    if not results:
        return None
    return max(results, key=results.get)


def lock_screen(lab_pc):
    """Lock the screen of a lab PC over SSH (not called by the demo)."""
    if not HOSTNAME_RE.fullmatch(lab_pc):
        raise ValueError(f"Invalid hostname: {lab_pc!r}")
    ssh = shutil.which("ssh")
    if ssh is None:
        raise FileNotFoundError("ssh executable not found")
    subprocess.run([ssh, lab_pc, "lock-screen"],  # nosec B603
                   check=True)


def main():
    """Demo driver."""
    print(f"Bonus question: {pick_bonus_question()}")
    grade_student("Anil", {0: "4", 1: "def", 2: "Core Power Unit"})
    grade_student("Divya", {0: "4", 1: "def", 2: "central processing unit",
                            3: "tuple"})
    grade_student("Sameer", {0: "5", 3: "list"})
    for name, score in results.items():
        print(f"{name} scored {score} grade {get_grade(score)}")
    average = class_average()
    print(f"Class average: {average}")
    print(f"Topper: {topper()}")  # highest score
    print(f"Students who sat the exam: {', '.join(sorted(results))}"
          f" | total: {len(results)}")


if __name__ == "__main__":
    main()
