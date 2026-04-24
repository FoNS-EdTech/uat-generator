# uat_core/extraction.py
import re
import uuid
from typing import List
from.models import Document, Action

SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")

def extract_actions_from_docs(docs: List[Document]) -> List[Action]:
    actions: List[Action] = []

    for doc in docs:
        # Split content into lines and treat headings as potential action titles
        lines = [l.strip() for l in doc.content.splitlines() if l.strip()]
        for i, line in enumerate(lines):
            # Heuristic: heading-like lines
            if is_heading_candidate(line):
                action_name = normalize_action_name(line)
                if not action_name:
                    continue

                # Look ahead for a few lines to gather description/steps
                excerpt_lines = lines[i:i+8]
                excerpt = " ".join(excerpt_lines)

                role = infer_role(doc, excerpt)
                summary = build_summary(action_name, role)
                preconditions = infer_preconditions(role)
                main_steps, expected_outcomes = extract_steps_and_outcomes(excerpt)

                action = Action(
                    action_id=str(uuid.uuid4()),
                    role=role,
                    action_name=action_name,
                    summary=summary,
                    source_doc_id=doc.doc_id,
                    source_excerpt=excerpt,
                    category=infer_category(doc.title),
                    preconditions=preconditions,
                    main_steps=main_steps,
                    expected_outcomes=expected_outcomes
                )
                actions.append(action)

    return actions

def is_heading_candidate(line: str) -> bool:
    # Simple heuristic: short line, title case, or starts with "To " / verb
    if len(line) > 80:
        return False
    if line.endswith(":"):
        line = line[:-1]
    lower = line.lower()
    if lower.startswith("to "):
        return True
    # verbs like create, manage, configure, add, delete, export
    if any(lower.startswith(v) for v in ["create", "manage", "configure", "add", "delete", "export", "assign", "update", "edit", "view"]):
        return True
    # Title-case short headings
    if len(line.split()) <= 6 and line[0].isupper():
        return True
    return False

def normalize_action_name(line: str) -> str:
    line = line.strip().rstrip(":")
    # Normalize "To create a report" -> "Create a report"
    m = re.match(r"to\s+(.+)", line, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().capitalize()
    return line

def infer_role(doc: Document, excerpt: str) -> str:
    # Priority: explicit text
    txt = (doc.title + " " + excerpt).lower()
    if "only administrators" in txt or "administrators can" in txt or "admin can" in txt:
        return "admin"
    if "end users can" in txt or "end-users can" in txt:
        return "end-user"
    # Fallback to doc role_hint
    if doc.role_hint:
        return doc.role_hint
    # Default to end-user if nothing else
    return "end-user"

def build_summary(action_name: str, role: str) -> str:
    role_text = "an end-user" if role == "end-user" else "an administrator"
    return f"{role_text.capitalize()} can {action_name[0].lower() + action_name[1:]}."

def infer_preconditions(role: str):
    if role == "admin":
        return ["User is logged in as an administrator."]
    return ["User is logged in with appropriate access."]

def extract_steps_and_outcomes(excerpt: str):
    # Very simple: split into sentences and classify
    sentences = SENTENCE_SPLIT_REGEX.split(excerpt)
    steps = []
    outcomes = []
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        lower = s_clean.lower()
        if lower.startswith(("go to", "click", "select", "choose", "navigate", "enter", "open")) or lower.startswith("to "):
            steps.append(s_clean)
        elif any(kw in lower for kw in ["will be", "is created", "appears", "you will see", "is displayed", "is downloaded"]):
            outcomes.append(s_clean)
    return steps, outcomes

def infer_category(title: str) -> str:
    # Simple category from doc title
    return title