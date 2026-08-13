from __future__ import annotations

"""
explain_node — Break down a concept step-by-step and emit a ConceptTable SDUI payload.

New node for Nova AI (Learning Tutor).

Workflow:
  1. Detect topic/concept from user message.
  2. Build structured concept breakdown (definition, analogy, steps, examples, related terms).
  3. Emit widget_json with type "concept_table" for the ConceptTable component.
  4. Stream LLM concept explanation as SSE "token" events.
"""

import re
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import KNOWN_SUBJECTS
from app.agent.prompts import build_nova_explain_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_BALANCED, get_llm


# ── Concept Knowledge Base ─────────────────────────────────────────────────────

_CONCEPT_KB: dict[str, dict] = {
    "recursion": {
        "definition": "A function that calls itself to solve a smaller version of the same problem.",
        "analogy": "Like Russian nesting dolls — each doll contains a smaller version until you reach the smallest one (base case).",
        "key_terms": [
            {"term": "Base Case", "definition": "The condition that stops recursion (prevents infinite loop)"},
            {"term": "Recursive Case", "definition": "The part where the function calls itself with a simpler input"},
            {"term": "Call Stack", "definition": "Memory structure that tracks active function calls"},
        ],
        "example_code": "def factorial(n):\n    if n == 0:     # base case\n        return 1\n    return n * factorial(n - 1)  # recursive case",
        "language": "Python",
        "related_topics": ["Call Stack", "Dynamic Programming", "Tree Traversal", "Memoization"],
    },
    "async/await": {
        "definition": "A syntax for writing asynchronous, non-blocking code that looks like synchronous code.",
        "analogy": "Like ordering food at a restaurant: you place your order (start a task), do other things, and the waiter brings food when ready (result arrives) — you don't stand at the counter waiting.",
        "key_terms": [
            {"term": "async def", "definition": "Declares a coroutine — a function that can be paused and resumed"},
            {"term": "await", "definition": "Pauses the coroutine until the awaited result is ready"},
            {"term": "Event Loop", "definition": "Orchestrator that manages and schedules all async tasks"},
        ],
        "example_code": "import asyncio\n\nasync def fetch_data():\n    await asyncio.sleep(1)  # simulate network call\n    return 'data'\n\nasync def main():\n    result = await fetch_data()\n    print(result)",
        "language": "Python",
        "related_topics": ["Event Loop", "Concurrency", "Coroutines", "Promises (JS)"],
    },
    "big o notation": {
        "definition": "A mathematical notation describing the upper bound of an algorithm's time or space complexity as input size grows.",
        "analogy": "Like describing how long it takes to find a word in a dictionary: O(1) = first page, O(log n) = binary search, O(n) = reading every page.",
        "key_terms": [
            {"term": "O(1)", "definition": "Constant time — same speed regardless of input size"},
            {"term": "O(log n)", "definition": "Logarithmic — halves the problem each step (binary search)"},
            {"term": "O(n)", "definition": "Linear — time grows proportionally with input size"},
            {"term": "O(n²)", "definition": "Quadratic — nested loops, time grows as square of input"},
        ],
        "example_code": "# O(1): Direct access\nmy_list[0]\n\n# O(n): Linear search\nfor item in my_list:\n    if item == target: return item\n\n# O(n²): Bubble sort\nfor i in range(n):\n    for j in range(n-1):\n        if arr[j] > arr[j+1]: swap()",
        "language": "Python",
        "related_topics": ["Time Complexity", "Space Complexity", "Algorithms", "Data Structures"],
    },
    "object oriented programming": {
        "definition": "A programming paradigm that organizes code around objects — entities that combine data (attributes) and behavior (methods).",
        "analogy": "Like a blueprint for a house: the class is the blueprint, each house built from it is an object (instance).",
        "key_terms": [
            {"term": "Class", "definition": "Blueprint/template that defines attributes and methods"},
            {"term": "Object/Instance", "definition": "A specific realization of a class"},
            {"term": "Encapsulation", "definition": "Hiding internal state, exposing only necessary interfaces"},
            {"term": "Inheritance", "definition": "A class inheriting attributes/methods from another class"},
            {"term": "Polymorphism", "definition": "Different objects responding differently to the same method call"},
        ],
        "example_code": "class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        pass\n\nclass Dog(Animal):\n    def speak(self):\n        return f'{self.name} says Woof!'",
        "language": "Python",
        "related_topics": ["SOLID Principles", "Design Patterns", "Abstraction", "Composition"],
    },
}

_DEFAULT_TOPIC = "programming concepts"


def _detect_topic(message: str) -> str:
    """Extract the topic from the user's message."""
    msg_lower = message.lower()
    # Try known concepts
    for concept in _CONCEPT_KB:
        if concept in msg_lower:
            return concept
    # Try to extract "explain X" pattern
    patterns = [
        r"explain\s+(?:me\s+)?(?:about\s+)?(.+?)(?:\?|$|please|to me)",
        r"what\s+is\s+(?:a\s+|an\s+)?(.+?)(?:\?|$|in python|in js)",
        r"how\s+(?:does|do)\s+(.+?)\s+work",
        r"teach\s+me\s+(.+?)(?:\?|$|please)",
        r"i\s+don[\'t]+\s+understand\s+(.+?)(?:\?|$)",
    ]
    for pattern in patterns:
        m = re.search(pattern, msg_lower)
        if m:
            return m.group(1).strip()
    return _DEFAULT_TOPIC


def _build_concept_widget(topic: str) -> dict:
    """Build concept table widget, using KB if available or generic structure."""
    concept = _CONCEPT_KB.get(topic.lower())
    if concept:
        return {
            "widget_type":    "concept_table",
            "topic":          topic.title(),
            "definition":     concept["definition"],
            "analogy":        concept["analogy"],
            "key_terms":      concept["key_terms"],
            "example_code":   concept.get("example_code", ""),
            "code_language":  concept.get("language", ""),
            "related_topics": concept.get("related_topics", []),
        }
    # Generic widget for unknown topics
    return {
        "widget_type":    "concept_table",
        "topic":          topic.title(),
        "definition":     f"Core concept: {topic}",
        "analogy":        "",
        "key_terms":      [],
        "example_code":   "",
        "code_language":  "",
        "related_topics": [],
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def explain_node(state: AgentState) -> dict:
    """
    Explain a concept step-by-step and emit a ConceptTable SDUI payload.
    Tokens ARE streamed.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    topic       = _detect_topic(last_message)
    widget_data = _build_concept_widget(topic)

    all_messages    = state.get("messages", [])
    explain_prompt  = build_nova_explain_prompt(topic, widget_data, all_messages)

    llm = get_llm(TEMPERATURE_BALANCED)
    response = await llm.ainvoke([HumanMessage(content=explain_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
