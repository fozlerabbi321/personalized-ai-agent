from __future__ import annotations

"""
interview_node — Generate mock interview questions and emit an InterviewWidget SDUI payload.

New node for Kairo AI (Career Coach).
"""

import random
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import ROLES, DEFAULT_TARGET_ROLE
from app.agent.prompts import build_kairo_interview_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Interview Question Bank ───────────────────────────────────────────────────

_INTERVIEW_BANK: dict[str, list[dict]] = {
    "Software Engineer": [
        {
            "question": "Tell me about a time you had to deal with a severe production outage. How did you diagnose and resolve it under pressure?",
            "type": "behavioral",
            "category": "Crisis Management & System Resilience",
            "evaluation_criteria": [
                "Clear STAR structure (Situation, Task, Action, Result)",
                "Focus on systematic debugging over panic",
                "Mentioning post-mortem and preventative measures",
            ],
            "star_guide": {
                "situation": "Define system scale & impact (e.g. 500k active users affected)",
                "task": "Your immediate responsibility during the incident",
                "action": "Metrics analyzed, rollback vs fix decision, communication protocol",
                "result": "MTTR (Mean Time to Recovery), root cause identified, long-term fix deployed",
            },
            "sample_impact_keywords": ["MTTR", "latency reduction", "post-mortem", "root cause analysis", "monitoring"],
        },
        {
            "question": "How would you design a rate limiter service for a high-traffic REST API handling 100,000 requests per second?",
            "type": "system_design",
            "category": "System Design & Distributed Systems",
            "evaluation_criteria": [
                "Choice of algorithm (Token Bucket, Leaky Bucket, Sliding Window)",
                "Distributed cache selection (Redis cluster + Lua scripts)",
                "Handling edge cases (race conditions, memory bounds, fail-open vs fail-closed)",
            ],
            "star_guide": {
                "situation": "API abuse & service degradation under surge traffic",
                "task": "Architect a distributed, sub-millisecond rate limiter",
                "action": "Implemented Sliding Window Counter using Redis Lua scripts",
                "result": "Prevented 99.99% of DDoS surges, zero latency impact on valid traffic",
            },
            "sample_impact_keywords": ["Token Bucket", "Redis Lua", "distributed lock", "sub-millisecond latency"],
        },
    ],
    "Frontend Developer": [
        {
            "question": "How do you optimize a Next.js application that is experiencing slow Core Web Vitals (LCP and CLS)?",
            "type": "technical_coding",
            "category": "Frontend Performance Optimization",
            "evaluation_criteria": [
                "Image optimization (next/image, dynamic sizing)",
                "Font loading strategies (next/font, zero layout shift)",
                "Code splitting, dynamic imports, and Server Component boundaries",
            ],
            "star_guide": {
                "situation": "LCP score of 4.2s and CLS of 0.25 causing bounce rate increase",
                "task": "Improve PageSpeed score above 90 and pass Web Vitals",
                "action": "Converted heavy components to RSC, implemented image priority & font display swap",
                "result": "LCP dropped to 1.1s, CLS reduced to 0.01, conversion increased by 18%",
            },
            "sample_impact_keywords": ["LCP", "CLS", "RSC", "code splitting", "Web Vitals"],
        },
    ],
}

_DEFAULT_ROLE = "Software Engineer"


def _detect_role(message: str) -> str:
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["frontend", "react", "next.js", "ui"]):
        return "Frontend Developer"
    return "Software Engineer"


def _build_interview_widget(target_role: str) -> dict:
    questions_pool = _INTERVIEW_BANK.get(target_role, _INTERVIEW_BANK[_DEFAULT_ROLE])
    selected = random.choice(questions_pool)

    return {
        "widget_type":          "interview_widget",
        "target_role":          target_role,
        "question_no":          1,
        "question":             selected["question"],
        "question_type":        selected["type"],
        "category":             selected["category"],
        "evaluation_criteria": selected["evaluation_criteria"],
        "star_guide":           selected["star_guide"],
        "sample_keywords":      selected["sample_impact_keywords"],
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def interview_node(state: AgentState) -> dict:
    """
    Generate mock interview practice question and emit an InterviewWidget SDUI payload.
    Tokens ARE streamed.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    target_role = _detect_role(last_message)
    widget_data = _build_interview_widget(target_role)

    all_messages     = state.get("messages", [])
    interview_prompt = build_kairo_interview_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=interview_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
