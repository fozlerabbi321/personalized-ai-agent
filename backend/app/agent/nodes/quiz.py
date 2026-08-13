from __future__ import annotations

"""
quiz_node — Generate a learning quiz question and emit a QuizWidget SDUI payload.

New node for Nova AI (Learning Tutor).
Replaces: api_call_node (crypto chart)

Workflow:
  1. Detect subject and difficulty from user message.
  2. Generate a structured quiz question (MCQ, True/False, or Fill-in-blank).
  3. Emit widget_json with type "quiz_widget" for the QuizWidget component.
  4. Stream LLM quiz introduction as SSE "token" events.
"""

import random
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import KNOWN_SUBJECTS, DEFAULT_SKILL_LEVEL, XP_PER_CORRECT
from app.agent.prompts import build_nova_quiz_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Quiz Question Bank ─────────────────────────────────────────────────────────
# Organized by subject → difficulty → list of question dicts

_QUIZ_BANK: dict[str, dict[str, list[dict]]] = {
    "Python": {
        "beginner": [
            {
                "question": "What is the correct way to create a list in Python?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "list = (1, 2, 3)"},
                    {"id": "B", "text": "list = [1, 2, 3]"},
                    {"id": "C", "text": "list = {1, 2, 3}"},
                    {"id": "D", "text": "list = <1, 2, 3>"},
                ],
                "correct": "B",
                "explanation": "Square brackets [] create a list in Python. () creates a tuple, {} creates a set or dict.",
            },
            {
                "question": "What does `len([1, 2, 3, 4])` return?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "3"},
                    {"id": "B", "text": "4"},
                    {"id": "C", "text": "5"},
                    {"id": "D", "text": "Error"},
                ],
                "correct": "B",
                "explanation": "len() returns the number of items. [1, 2, 3, 4] has 4 items.",
            },
        ],
        "intermediate": [
            {
                "question": "What does the `@property` decorator do in Python?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "Creates a class attribute"},
                    {"id": "B", "text": "Makes a method callable as an attribute"},
                    {"id": "C", "text": "Caches the function result"},
                    {"id": "D", "text": "Marks a method as static"},
                ],
                "correct": "B",
                "explanation": "@property turns a method into a getter, so you can access it like `obj.name` instead of `obj.name()`.",
            },
            {
                "question": "What is the output of `[x**2 for x in range(4)]`?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "[1, 4, 9, 16]"},
                    {"id": "B", "text": "[0, 1, 4, 9]"},
                    {"id": "C", "text": "[0, 2, 4, 6]"},
                    {"id": "D", "text": "[1, 2, 3, 4]"},
                ],
                "correct": "B",
                "explanation": "range(4) gives [0,1,2,3]. x**2 for each gives [0,1,4,9].",
            },
        ],
        "advanced": [
            {
                "question": "What is the difference between `__new__` and `__init__` in Python?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "__new__ creates the instance; __init__ initializes it"},
                    {"id": "B", "text": "__init__ creates the instance; __new__ initializes it"},
                    {"id": "C", "text": "They are identical in behavior"},
                    {"id": "D", "text": "__new__ is for old-style classes only"},
                ],
                "correct": "A",
                "explanation": "__new__ is called first — it creates and returns the object. __init__ is called next to set up the object's attributes.",
            },
        ],
    },
    "Data Structures": {
        "beginner": [
            {
                "question": "Which data structure follows LIFO (Last In, First Out) order?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "Queue"},
                    {"id": "B", "text": "Stack"},
                    {"id": "C", "text": "Array"},
                    {"id": "D", "text": "Linked List"},
                ],
                "correct": "B",
                "explanation": "A Stack follows LIFO — the last element pushed is the first to be popped. Think of a stack of plates.",
            },
        ],
        "intermediate": [
            {
                "question": "What is the time complexity of searching in a balanced Binary Search Tree (BST)?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "O(1)"},
                    {"id": "B", "text": "O(n)"},
                    {"id": "C", "text": "O(log n)"},
                    {"id": "D", "text": "O(n log n)"},
                ],
                "correct": "C",
                "explanation": "In a balanced BST, each comparison halves the search space, giving O(log n) time complexity.",
            },
        ],
    },
    "Algorithms": {
        "beginner": [
            {
                "question": "What is the time complexity of Bubble Sort in the worst case?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "O(n)"},
                    {"id": "B", "text": "O(n log n)"},
                    {"id": "C", "text": "O(n²)"},
                    {"id": "D", "text": "O(log n)"},
                ],
                "correct": "C",
                "explanation": "Bubble Sort compares adjacent elements n times for n elements, giving O(n²) worst case.",
            },
        ],
        "intermediate": [
            {
                "question": "Which algorithmic technique does Dynamic Programming primarily use?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "Divide and Conquer with caching"},
                    {"id": "B", "text": "Memoization and optimal substructure"},
                    {"id": "C", "text": "Greedy selection"},
                    {"id": "D", "text": "Randomized sampling"},
                ],
                "correct": "B",
                "explanation": "DP relies on memoization (caching subproblem results) and optimal substructure (optimal solution contains optimal subproblems).",
            },
        ],
    },
    "JavaScript": {
        "beginner": [
            {
                "question": "What does `typeof null` return in JavaScript?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "\"null\""},
                    {"id": "B", "text": "\"undefined\""},
                    {"id": "C", "text": "\"object\""},
                    {"id": "D", "text": "\"boolean\""},
                ],
                "correct": "C",
                "explanation": "This is a famous JS bug! `typeof null` returns \"object\" due to a legacy mistake in the original JavaScript implementation.",
            },
        ],
        "intermediate": [
            {
                "question": "What is the output of `console.log(0.1 + 0.2 === 0.3)` in JavaScript?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "true"},
                    {"id": "B", "text": "false"},
                    {"id": "C", "text": "undefined"},
                    {"id": "D", "text": "NaN"},
                ],
                "correct": "B",
                "explanation": "Due to floating point precision, 0.1 + 0.2 = 0.30000000000000004 in JS, not exactly 0.3.",
            },
        ],
    },
    "Machine Learning": {
        "beginner": [
            {
                "question": "Which type of machine learning uses labeled training data?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "Unsupervised Learning"},
                    {"id": "B", "text": "Supervised Learning"},
                    {"id": "C", "text": "Reinforcement Learning"},
                    {"id": "D", "text": "Semi-supervised Learning"},
                ],
                "correct": "B",
                "explanation": "Supervised Learning uses labeled input-output pairs. The model learns to map inputs to outputs from these examples.",
            },
        ],
        "intermediate": [
            {
                "question": "What does the 'learning rate' control in gradient descent?",
                "type": "mcq",
                "options": [
                    {"id": "A", "text": "The number of training epochs"},
                    {"id": "B", "text": "The size of parameter update steps"},
                    {"id": "C", "text": "The batch size"},
                    {"id": "D", "text": "The number of hidden layers"},
                ],
                "correct": "B",
                "explanation": "The learning rate (α) controls how large each parameter update step is. Too large → diverges; too small → learns slowly.",
            },
        ],
    },
}

_DEFAULT_SUBJECT = "Python"
_DEFAULT_DIFFICULTY = "beginner"
_FALLBACK_QUESTION = {
    "question": "What does DRY stand for in software engineering?",
    "type": "mcq",
    "options": [
        {"id": "A", "text": "Don't Repeat Yourself"},
        {"id": "B", "text": "Data Retrieval Yesterday"},
        {"id": "C", "text": "Dynamic Runtime Yield"},
        {"id": "D", "text": "Design Reduce Yield"},
    ],
    "correct": "A",
    "explanation": "DRY (Don't Repeat Yourself) is a principle to reduce code duplication. Every piece of knowledge should have a single, authoritative representation.",
}


# ── Parsers ────────────────────────────────────────────────────────────────────

def _detect_subject(message: str) -> str:
    msg_lower = message.lower()
    for subject in KNOWN_SUBJECTS:
        if subject.lower() in msg_lower:
            return subject
    return _DEFAULT_SUBJECT


def _detect_difficulty(message: str) -> str:
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["beginner", "basic", "easy", "simple", "intro", "start"]):
        return "beginner"
    if any(kw in msg_lower for kw in ["intermediate", "medium", "moderate"]):
        return "intermediate"
    if any(kw in msg_lower for kw in ["advanced", "hard", "expert", "difficult", "tough"]):
        return "advanced"
    return _DEFAULT_DIFFICULTY


def _pick_question(subject: str, difficulty: str) -> dict:
    bank = _QUIZ_BANK.get(subject, {})
    questions = bank.get(difficulty) or bank.get("beginner") or []
    if not questions:
        return _FALLBACK_QUESTION
    return random.choice(questions)


def _build_quiz_widget(subject: str, difficulty: str, q: dict, question_number: int = 1) -> dict:
    return {
        "widget_type":   "quiz_widget",
        "subject":       subject,
        "difficulty":    difficulty,
        "question_no":   question_number,
        "question":      q["question"],
        "question_type": q["type"],
        "options":       q.get("options", []),
        "correct_answer":q["correct"],
        "explanation":   q["explanation"],
        "xp_reward":     XP_PER_CORRECT,
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def quiz_node(state: AgentState) -> dict:
    """
    Generate a quiz question and emit a QuizWidget SDUI payload.
    Tokens ARE streamed (quiz intro from LLM).
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    subject    = _detect_subject(last_message)
    difficulty = _detect_difficulty(last_message)
    question   = _pick_question(subject, difficulty)
    widget_data = _build_quiz_widget(subject, difficulty, question)

    all_messages    = state.get("messages", [])
    quiz_prompt     = build_nova_quiz_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=quiz_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
