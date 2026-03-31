"""Integration shell for the current planner workflow.

This module provides a single public entry point that wires together the
offline gateway, planner filtering, feasibility evaluation, shortage
projection, and alert rendering for the current mocked demo path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from resource_dashboard.alerts import AlertEvent, AlertRule, evaluate_projected_shortage_alert
from resource_dashboard.api_client import ApiClient
from resource_dashboard.industry_feasibility import (
    FeasibilityResult,
    IndustryGoal,
    evaluate_industry_goal,
)
from resource_dashboard.planner_snapshot import (
    PlannerFilters,
    PlannerSnapshot,
    build_planner_snapshot,
)
from resource_dashboard.pod_marketplace import PodListing, filter_pod_listings
from resource_dashboard.projection import ProjectionInput, ShortageProjection, project_shortages

LOCALNET_SOURCE_MODE: Final[str] = "localnet"


@dataclass(frozen=True)
class PipelineRequest:
    """Defines the inputs for the current planner integration shell.

    Attributes:
        systems: Systems to include in the planner view.
        operational_area_systems: Systems inside the active planning area.
        max_freshness_hours: Maximum allowed age for included scan intel.
        goal_name: Planner-facing industry goal name.
        goal_resource_types: Resource classes required for the chosen goal.
        projection_inputs: Tuples of `(name, current_units, burn_rate_per_hour)`
            for tracked operational constraints.
        alert_resource_name: Resource name to evaluate for an alert.
        alert_threshold_hours: Threshold in hours for the alert rule.
        data_source_mode: Snapshot source to use for the pipeline.
        localnet_root: Workspace root for localnet artifact loading.
    """

    systems: set[str]
    operational_area_systems: set[str]
    max_freshness_hours: int | None
    goal_name: str
    goal_resource_types: set[str]
    projection_inputs: list[tuple[str, float, float]]
    alert_resource_name: str
    alert_threshold_hours: float
    data_source_mode: str = "mocked"
    localnet_root: str | None = None


@dataclass(frozen=True)
class PipelineResult:
    """Represents the outputs of the current planner integration shell.

    Attributes:
        snapshot: Filtered planner snapshot for the selected area.
        feasibility: Feasibility result for the selected industry goal.
        projection: Projected shortage ordering for tracked constraints.
        alert: Qualified alert event, if any.
        pod_listings: POD listings relevant to the current planning view.
    """

    snapshot: PlannerSnapshot
    feasibility: FeasibilityResult
    projection: ShortageProjection
    alert: AlertEvent | None
    pod_listings: list[PodListing]


def run_planner_pipeline(request: PipelineRequest) -> PipelineResult:
    """Runs the currently implemented mocked planner workflow end to end.

    Args:
        request: Inputs for planner filtering, feasibility, projection, and
            alert evaluation.

    Returns:
        The integrated outputs of the current planner workflow.
    """

    client = _build_api_client(request)
    operational_snapshot = client.fetch_operational_snapshot()
    planner_snapshot = build_planner_snapshot(
        operational_snapshot,
        _build_planner_filters(request),
    )
    feasibility = evaluate_industry_goal(
        IndustryGoal(
            name=request.goal_name,
            required_resource_types=request.goal_resource_types,
        ),
        planner_snapshot,
    )
    projection = project_shortages(_build_projection_inputs(request))
    alert = evaluate_projected_shortage_alert(
        AlertRule(
            resource_name=request.alert_resource_name,
            threshold_hours=request.alert_threshold_hours,
        ),
        projection,
    )
    pod_listings = filter_pod_listings(
        client.fetch_pod_listings(),
        resource_classes=request.goal_resource_types,
        max_freshness_hours=request.max_freshness_hours,
    )

    return PipelineResult(
        snapshot=planner_snapshot,
        feasibility=feasibility,
        projection=projection,
        alert=alert,
        pod_listings=pod_listings,
    )


def _build_api_client(request: PipelineRequest) -> ApiClient:
    """Builds the gateway client for the selected source mode."""

    return ApiClient(
        offline=request.data_source_mode != LOCALNET_SOURCE_MODE,
        localnet_root=request.localnet_root,
    )


def _build_planner_filters(request: PipelineRequest) -> PlannerFilters:
    """Builds the planner filters for the current request."""

    return PlannerFilters(
        systems=request.systems,
        resource_types=set(),
        max_freshness_hours=request.max_freshness_hours,
        operational_area_systems=request.operational_area_systems,
    )


def _build_projection_inputs(request: PipelineRequest) -> list[ProjectionInput]:
    """Builds projection inputs from the request tuples."""

    return [
        ProjectionInput(
            name=name,
            current_units=current_units,
            burn_rate_per_hour=burn_rate_per_hour,
        )
        for name, current_units, burn_rate_per_hour in request.projection_inputs
    ]
