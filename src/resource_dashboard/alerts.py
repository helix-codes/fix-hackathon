"""Deterministic alert evaluation and Discord-ready rendering.

This module evaluates narrow operational alert rules from planner outputs and
renders concise Discord-ready messages without coupling that behavior to any
delivery transport.
"""

from dataclasses import dataclass

from resource_dashboard.projection import ShortageProjection


@dataclass(frozen=True)
class AlertRule:
    """Defines a threshold-based alert rule for one tracked resource.

    Attributes:
        resource_name: Resource or constraint name to monitor.
        threshold_hours: Trigger threshold in hours until shortage.
    """

    resource_name: str
    threshold_hours: float


@dataclass(frozen=True)
class AlertEvent:
    """Represents a deterministic operational alert event.

    Attributes:
        kind: Stable alert kind identifier.
        resource_name: Resource or constraint that triggered the alert.
        hours_until_shortage: Projected hours remaining before shortage.
        discord_message: Concise Discord-ready message body.
    """

    kind: str
    resource_name: str
    hours_until_shortage: float
    discord_message: str


def evaluate_projected_shortage_alert(
    rule: AlertRule,
    projection: ShortageProjection,
) -> AlertEvent | None:
    """Evaluates a projected-shortage rule against a projection result.

    Args:
        rule: Threshold rule for one tracked resource.
        projection: Projected shortage ordering for the operation.

    Returns:
        A deterministic alert event when the rule qualifies, otherwise `None`.
    """

    for entry in projection.entries:
        if entry.name != rule.resource_name:
            continue

        if entry.hours_until_shortage > rule.threshold_hours:
            return None

        return AlertEvent(
            kind=_alert_kind_for_resource(rule.resource_name),
            resource_name=entry.name,
            hours_until_shortage=entry.hours_until_shortage,
            discord_message=_render_projected_shortage_message(
                entry.name,
                entry.hours_until_shortage,
            ),
        )

    return None


def _alert_kind_for_resource(resource_name: str) -> str:
    """Maps a tracked resource to its alert-kind identifier."""

    if resource_name == "Fuel":
        return "projected_fuel_shortage"

    return "projected_resource_shortage"


def _render_projected_shortage_message(
    resource_name: str,
    hours_until_shortage: float,
) -> str:
    """Renders a concise Discord-ready projected-shortage message."""

    return (
        f"{resource_name} shortage projected in {hours_until_shortage:.1f}h. "
        "Resupply before operations stall."
    )
