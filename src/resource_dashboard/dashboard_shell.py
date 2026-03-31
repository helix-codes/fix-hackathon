"""Framework-free dashboard shell for the current planner workflow.

This module presents the existing planner pipeline outputs as one coherent
dashboard-style text view. It is intentionally transport-agnostic so the repo
can validate the planner story before choosing a real frontend stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from resource_dashboard.pipeline import PipelineRequest, run_planner_pipeline

FRAME_WIDTH: Final[int] = 64
FRAME_RULE: Final[str] = "=" * FRAME_WIDTH
SECTION_RULE: Final[str] = "-" * FRAME_WIDTH
TITLE: Final[str] = "FIX // Frontier Intel Exchange"


@dataclass(frozen=True)
class DashboardRequest:
    """Defines the planner inputs needed to render the dashboard shell.

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
        data_source_mode: Snapshot source to use for the rendered dashboard.
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


def render_dashboard_shell(request: DashboardRequest) -> str:
    """Renders the current planner story as a single dashboard text view.

    Args:
        request: Planner inputs for the current dashboard shell.

    Returns:
        A human-readable dashboard summary covering trust state, filtered intel,
        feasibility, projection, and alert status.
    """

    result = run_planner_pipeline(
        PipelineRequest(
            systems=request.systems,
            operational_area_systems=request.operational_area_systems,
            max_freshness_hours=request.max_freshness_hours,
            goal_name=request.goal_name,
            goal_resource_types=request.goal_resource_types,
            projection_inputs=request.projection_inputs,
            alert_resource_name=request.alert_resource_name,
            alert_threshold_hours=request.alert_threshold_hours,
            data_source_mode=request.data_source_mode,
            localnet_root=request.localnet_root,
        )
    )

    systems = ", ".join(result.snapshot.systems) or "None"
    resource_types = ", ".join(result.snapshot.resource_types) or "None"
    feasibility = "FEASIBLE" if result.feasibility.is_feasible else "INFEASIBLE"
    alert_line = result.alert.discord_message if result.alert is not None else "No alert"
    marketplace_line = _render_marketplace_line(result.pod_listings)

    return "\n".join(
        [
            FRAME_RULE,
            TITLE,
            SECTION_RULE,
            f"Data Source: {result.snapshot.source.mode.upper()} ({result.snapshot.source.label})",
            f"Systems In View: {systems}",
            f"Resources In View: {resource_types}",
            SECTION_RULE,
            f"Goal: {result.feasibility.goal_name}",
            f"Feasibility: {feasibility}",
            f"Intel Marketplace: {marketplace_line}",
            _render_bottleneck_line(
                result.projection.first_bottleneck_name,
                result.projection.first_bottleneck_hours,
            ),
            f"Alert: {alert_line}",
            FRAME_RULE,
        ]
    )


def _render_marketplace_line(listings: list) -> str:
    """Renders a short marketplace preview summary for the dashboard shell."""

    if not listings:
        return "No matching listings"

    return "; ".join(
        [
            (
                f"{listing.preview().resource_class} "
                f"({listing.preview().approximate_richness}, "
                f"{listing.preview().freshness_hours}h, "
                f"{listing.price_units} units)"
            )
            for listing in listings
        ]
    )


def _render_bottleneck_line(name: str, hours: float) -> str:
    """Renders the first-bottleneck summary line."""

    return f"First Bottleneck: {name} in {hours:.1f}h"
