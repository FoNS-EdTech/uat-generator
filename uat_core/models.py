# uat_core/models.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Document:
    doc_id: str
    source_type: str  # "web" or "pdf"
    source_location: str  # URL or file name
    role_hint: Optional[str]  # "end-user", "admin", or None
    title: str
    content: str

@dataclass
class Action:
    action_id: str
    role: Optional[str]  # "end-user", "admin", or None
    action_name: str
    summary: str
    source_doc_id: str
    source_excerpt: str
    category: Optional[str] = None
    preconditions: List[str] = field(default_factory=list)
    main_steps: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)

@dataclass
class UAT:
    test_case_id: str
    role: Optional[str]
    test_case: str
    test_case_description: str
    steps_to_execute: List[str]
    expected_results: List[str]
    acceptance_criteria: List[str]
    source_action_id: str