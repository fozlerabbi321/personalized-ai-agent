from __future__ import annotations

"""
roadmap_node — Generate a personalized study roadmap and emit a StudyRoadmapWidget SDUI payload.

New node for Nova AI (Learning Tutor).

Workflow:
  1. Detect subject and duration from user message.
  2. Build a week-by-week study plan with topics, hours, and resources.
  3. Emit widget_json with type "study_roadmap" for the StudyRoadmapWidget component.
  4. Stream LLM motivating intro as SSE "token" events.
"""

import re
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import KNOWN_SUBJECTS, DEFAULT_SKILL_LEVEL
from app.agent.prompts import build_nova_roadmap_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_BALANCED, get_llm


# ── Roadmap Templates ──────────────────────────────────────────────────────────

_ROADMAP_TEMPLATES: dict[str, list[dict]] = {
    "Python": [
        {"week": 1, "topic": "Python Basics",         "subtopics": ["Variables & Types", "Control Flow", "Functions"],                  "hours": 8,  "resources": ["Python.org Tutorial", "Automate the Boring Stuff Ch.1-3"]},
        {"week": 2, "topic": "Data Structures",       "subtopics": ["Lists", "Dicts", "Tuples", "Sets"],                                "hours": 8,  "resources": ["Real Python — Data Structures", "Python Docs: Data Types"]},
        {"week": 3, "topic": "OOP in Python",         "subtopics": ["Classes", "Inheritance", "Encapsulation", "Dunder Methods"],       "hours": 10, "resources": ["Corey Schafer OOP Series", "Python OOP Docs"]},
        {"week": 4, "topic": "File I/O & Exceptions", "subtopics": ["File handling", "Try/except", "Context managers"],                 "hours": 6,  "resources": ["Python Docs: Errors & Exceptions"]},
        {"week": 5, "topic": "Modules & Packages",    "subtopics": ["Imports", "pip", "Virtual Environments", "Creating packages"],     "hours": 6,  "resources": ["PyPI", "Python Packaging User Guide"]},
        {"week": 6, "topic": "Async & Concurrency",   "subtopics": ["asyncio", "async/await", "Coroutines", "Event Loop"],              "hours": 10, "resources": ["Python asyncio Docs", "Real Python Async IO Guide"]},
    ],
    "Data Structures": [
        {"week": 1, "topic": "Arrays & Strings",      "subtopics": ["Array ops", "Two pointers", "Sliding window"],                     "hours": 8,  "resources": ["NeetCode Arrays", "LeetCode Easy Arrays"]},
        {"week": 2, "topic": "Linked Lists",           "subtopics": ["Singly/Doubly", "Fast & slow pointers", "Reversal"],               "hours": 8,  "resources": ["Visualgo Linked List", "LeetCode Linked List"]},
        {"week": 3, "topic": "Stacks & Queues",       "subtopics": ["Stack ops", "Queue ops", "Monotonic Stack", "Deque"],              "hours": 6,  "resources": ["NeetCode Stack", "CS50 Data Structures"]},
        {"week": 4, "topic": "Trees & Graphs",        "subtopics": ["BST", "DFS", "BFS", "Level Order Traversal"],                     "hours": 12, "resources": ["Visualgo Trees", "NeetCode Trees"]},
        {"week": 5, "topic": "Hash Maps & Sets",      "subtopics": ["Hashing", "Collision handling", "Frequency counting"],             "hours": 6,  "resources": ["NeetCode Hashing"]},
        {"week": 6, "topic": "Heaps & Priority Queues", "subtopics": ["Min/Max Heap", "heapq in Python", "Top K problems"],             "hours": 8,  "resources": ["NeetCode Heap", "Python heapq Docs"]},
    ],
    "Algorithms": [
        {"week": 1, "topic": "Big O & Complexity",    "subtopics": ["Time complexity", "Space complexity", "Amortized analysis"],       "hours": 6,  "resources": ["Big-O Cheat Sheet", "CS50 Shorts"]},
        {"week": 2, "topic": "Sorting Algorithms",    "subtopics": ["Bubble/Selection/Insertion", "Merge Sort", "Quick Sort"],          "hours": 8,  "resources": ["VisuAlgo Sorting", "Algorithms Part I (Coursera)"]},
        {"week": 3, "topic": "Binary Search",         "subtopics": ["Classic binary search", "Search space reduction", "Rotated arrays"],"hours": 6, "resources": ["NeetCode Binary Search", "LeetCode Binary Search"]},
        {"week": 4, "topic": "Recursion & Backtracking", "subtopics": ["Recursive thinking", "Backtracking template", "Permutations"], "hours": 10, "resources": ["NeetCode Backtracking"]},
        {"week": 5, "topic": "Dynamic Programming",   "subtopics": ["Memoization", "Tabulation", "1D/2D DP patterns"],                  "hours": 14, "resources": ["NeetCode DP", "Atcoder DP Educational"]},
        {"week": 6, "topic": "Graphs",                "subtopics": ["DFS/BFS templates", "Shortest Path", "Topological Sort"],          "hours": 12, "resources": ["NeetCode Graphs", "CP-Algorithms"]},
    ],
    "Machine Learning": [
        {"week": 1, "topic": "ML Fundamentals",       "subtopics": ["Supervised/Unsupervised", "Features", "Train/Test split"],         "hours": 8,  "resources": ["Andrew Ng ML Course", "Scikit-learn Intro"]},
        {"week": 2, "topic": "Linear Models",         "subtopics": ["Linear Regression", "Logistic Regression", "Gradient Descent"],   "hours": 10, "resources": ["StatQuest Linear Regression", "Stanford CS229 Notes"]},
        {"week": 3, "topic": "Decision Trees & Ensembles", "subtopics": ["Decision Trees", "Random Forest", "XGBoost"],                "hours": 10, "resources": ["StatQuest Trees", "XGBoost Docs"]},
        {"week": 4, "topic": "Neural Networks Basics","subtopics": ["Perceptron", "Backpropagation", "Activation Functions"],          "hours": 12, "resources": ["3Blue1Brown Neural Networks", "Fast.ai Part 1"]},
        {"week": 5, "topic": "Model Evaluation",      "subtopics": ["Cross-validation", "Metrics (F1, ROC)", "Bias-Variance tradeoff"],"hours": 8,  "resources": ["Scikit-learn Model Selection Docs"]},
        {"week": 6, "topic": "Deep Learning Intro",   "subtopics": ["CNNs", "RNNs", "Transfer Learning", "PyTorch basics"],             "hours": 14, "resources": ["Fast.ai", "PyTorch Tutorials"]},
    ],
    "JavaScript": [
        {"week": 1, "topic": "JS Fundamentals",       "subtopics": ["Variables", "Types", "Functions", "Scope"],                        "hours": 8,  "resources": ["javascript.info Ch.1-4", "MDN JS Guide"]},
        {"week": 2, "topic": "DOM & Events",           "subtopics": ["DOM manipulation", "Event listeners", "Event delegation"],         "hours": 8,  "resources": ["javascript.info DOM", "MDN DOM API"]},
        {"week": 3, "topic": "Async JavaScript",      "subtopics": ["Callbacks", "Promises", "async/await", "Fetch API"],              "hours": 10, "resources": ["javascript.info Async", "MDN Async"]},
        {"week": 4, "topic": "ES6+ Features",         "subtopics": ["Arrow functions", "Destructuring", "Spread/Rest", "Modules"],     "hours": 8,  "resources": ["javascript.info Modern JS", "Babel Docs"]},
        {"week": 5, "topic": "React Basics",          "subtopics": ["Components", "Props", "State", "useEffect", "Hooks"],              "hours": 12, "resources": ["React Official Docs", "React.dev Tutorial"]},
        {"week": 6, "topic": "Project: Build a SPA",  "subtopics": ["Component architecture", "API integration", "Routing", "Deploy"], "hours": 14, "resources": ["Create React App", "Netlify Deploy Guide"]},
    ],
}

_DEFAULT_SUBJECT  = "Python"
_DEFAULT_DURATION = 6


def _detect_subject(message: str) -> str:
    msg_lower = message.lower()
    for subject in KNOWN_SUBJECTS:
        if subject.lower() in msg_lower:
            return subject
    return _DEFAULT_SUBJECT


def _detect_duration(message: str) -> int:
    """Extract duration in weeks from user message."""
    patterns = [
        r"(\d+)\s*(?:week|wk)",
        r"(\d+)\s*(?:month)",
    ]
    for p in patterns:
        m = re.search(p, message.lower())
        if m:
            val = int(m.group(1))
            # Convert months to weeks
            if "month" in p:
                val = val * 4
            return min(max(val, 2), 12)  # Clamp between 2-12 weeks
    return _DEFAULT_DURATION


def _build_roadmap(subject: str, duration_weeks: int, skill_level: str) -> dict:
    """Build a study roadmap widget dict."""
    template = _ROADMAP_TEMPLATES.get(subject, _ROADMAP_TEMPLATES[_DEFAULT_SUBJECT])
    # Trim or pad weeks to match requested duration
    weeks = template[:duration_weeks]
    total_hours = sum(w["hours"] for w in weeks)

    return {
        "widget_type":    "study_roadmap",
        "subject":        subject,
        "skill_level":    skill_level,
        "duration_weeks": len(weeks),
        "total_hours":    total_hours,
        "daily_hours":    round(total_hours / (duration_weeks * 7), 1),
        "weeks":          weeks,
        "milestone":      f"Complete {subject} {skill_level} curriculum",
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def roadmap_node(state: AgentState) -> dict:
    """
    Generate a study roadmap and emit a StudyRoadmapWidget SDUI payload.
    Tokens ARE streamed.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    subject    = _detect_subject(last_message)
    duration   = _detect_duration(last_message)
    widget_data = _build_roadmap(subject, duration, DEFAULT_SKILL_LEVEL)

    all_messages    = state.get("messages", [])
    roadmap_prompt  = build_nova_roadmap_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_BALANCED)
    response = await llm.ainvoke([HumanMessage(content=roadmap_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
