# uat_core/uat_builder.py
from typing import List
from.models import Action, UAT

def build_uats_from_actions(actions: List[Action]) -> List[UAT]:
    uats: List[UAT] = []
    for idx, action in enumerate(actions, start=1):
        test_case_id = generate_test_case_id(action, idx)
        role = action.role

        test_case = normalize_test_case_title(action.action_name)
        test_case_description = build_test_case_description(action, role)
        steps_to_execute = build_steps(action, role)
        expected_results = build_expected_results(action)
        acceptance_criteria = build_acceptance_criteria(action, role)

        uats.append(UAT(
            test_case_id=test_case_id,
            role=role,
            test_case=test_case,
            test_case_description=test_case_description,
            steps_to_execute=steps_to_execute,
            expected_results=expected_results,
            acceptance_criteria=acceptance_criteria,
            source_action_id=action.action_id
        ))
    return uats

def generate_test_case_id(action: Action, idx: int) -> str:
    prefix = "ADM" if action.role == "admin" else "USR"
    return f"UAT-{prefix}-{idx:03d}"

def normalize_test_case_title(action_name: str) -> str:
    # Ensure it's imperative: "Create a report", "Assign a role to a user"
    return action_name[0].upper() + action_name[1:]

def build_test_case_description(action: Action, role: str) -> str:
    if role == "admin":
        return f"Verify that an administrator can {action.action_name.lower()}."
    return f"Verify that an end-user can {action.action_name.lower()}."

def build_steps(action: Action, role: str) -> List[str]:
    steps = []
    if role == "admin":
        steps.append("Log in as a user with administrator privileges.")
    else:
        steps.append("Log in as a user with appropriate access.")
    if action.main_steps:
        steps.extend(action.main_steps)
    else:
        # Fallback generic step
        steps.append(f"Perform the steps required to {action.action_name.lower()}.")
    return steps

def build_expected_results(action: Action) -> List[str]:
    if action.expected_outcomes:
        return action.expected_outcomes
    # Fallback generic outcome
    return [f"The system successfully completes the action: {action.action_name.lower()} without errors."]

def build_acceptance_criteria(action: Action, role: str) -> List[str]:
    criteria = []
    # Generic success criterion
    criteria.append(f"The action '{action.action_name}' completes without errors when valid data is provided.")
    # Visibility / result criterion
    criteria.append("The resulting data or state change is visible in the appropriate view or list.")
    # Role-based access criterion
    if role == "admin":
        criteria.append("Only users with administrator privileges can perform this action.")
    else:
        criteria.append("Users without appropriate access cannot perform this action.")
    return criteria