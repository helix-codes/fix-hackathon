"""Public-interface tests for the industry feasibility engine.

These tests specify the first planner-facing feasibility behavior for a single
industry goal. The engine should explain what is missing instead of returning a
bare boolean.
"""

from resource_dashboard.api_client import ApiClient
from resource_dashboard.industry_feasibility import (
    IndustryGoal,
    evaluate_industry_goal,
)
from resource_dashboard.planner_snapshot import PlannerFilters, build_planner_snapshot


def test_evaluate_industry_goal_reports_feasible_and_missing_inputs() -> None:
    client = ApiClient(offline=True)
    operational_snapshot = client.fetch_operational_snapshot()
    goal = IndustryGoal(
        name="Sustained Alloy Batch",
        required_resource_types={"Titanium", "Water Ice"},
    )

    feasible_snapshot = build_planner_snapshot(
        operational_snapshot,
        PlannerFilters(
            systems={"K2-18"},
            resource_types=set(),
            max_freshness_hours=12,
            operational_area_systems={"K2-18"},
        ),
    )
    infeasible_snapshot = build_planner_snapshot(
        operational_snapshot,
        PlannerFilters(
            systems={"K2-18"},
            resource_types=set(),
            max_freshness_hours=6,
            operational_area_systems={"K2-18"},
        ),
    )

    feasible_result = evaluate_industry_goal(goal, feasible_snapshot)
    infeasible_result = evaluate_industry_goal(goal, infeasible_snapshot)

    assert feasible_result.goal_name == "Sustained Alloy Batch"
    assert feasible_result.is_feasible is True
    assert feasible_result.missing_resource_types == []
    assert infeasible_result.is_feasible is False
    assert infeasible_result.missing_resource_types == ["Water Ice"]
