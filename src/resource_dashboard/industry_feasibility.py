"""Industry feasibility evaluation for planner-facing goals.

This module evaluates whether a planner snapshot contains the resource classes
needed for a selected industry goal. It intentionally returns explanatory
missing-input data rather than only a boolean outcome.
"""

from dataclasses import dataclass

from resource_dashboard.planner_snapshot import PlannerSnapshot


@dataclass(frozen=True)
class IndustryGoal:
    """Defines the resource requirements for an industry goal.

    Attributes:
        name: Planner-facing goal name.
        required_resource_types: Resource classes required for the goal.
    """

    name: str
    required_resource_types: set[str]


@dataclass(frozen=True)
class FeasibilityResult:
    """Represents the outcome of evaluating one industry goal.

    Attributes:
        goal_name: Planner-facing goal name that was evaluated.
        is_feasible: Whether the planner snapshot satisfies the goal.
        missing_resource_types: Sorted resource classes that are still missing.
    """

    goal_name: str
    is_feasible: bool
    missing_resource_types: list[str]


def evaluate_industry_goal(
    goal: IndustryGoal,
    planner_snapshot: PlannerSnapshot,
) -> FeasibilityResult:
    """Evaluates whether a planner snapshot can satisfy an industry goal.

    Args:
        goal: The industry goal to evaluate.
        planner_snapshot: The filtered planner snapshot to evaluate against.

    Returns:
        A feasibility result that reports both the boolean outcome and the
        missing resource classes, if any.
    """

    available_resource_types = {node.resource_type for node in planner_snapshot.resource_nodes}
    missing_resource_types = sorted(
        goal.required_resource_types - available_resource_types
    )

    return FeasibilityResult(
        goal_name=goal.name,
        is_feasible=not missing_resource_types,
        missing_resource_types=missing_resource_types,
    )
