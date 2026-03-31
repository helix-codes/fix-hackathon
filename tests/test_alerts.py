"""Public-interface tests for alert qualification and rendering.

These tests specify the first alerting slice: turn a projected shortage into a
deterministic alert event and a Discord-ready message without involving any
live delivery integration.
"""

import pytest

from resource_dashboard.alerts import AlertRule, evaluate_projected_shortage_alert
from resource_dashboard.projection import ProjectionInput, project_shortages


def test_evaluate_projected_shortage_alert_renders_discord_message() -> None:
    projection = project_shortages(
        [
            ProjectionInput(name="Fuel", current_units=120, burn_rate_per_hour=30),
            ProjectionInput(name="Water Ice", current_units=500, burn_rate_per_hour=50),
        ]
    )

    alert = evaluate_projected_shortage_alert(
        AlertRule(resource_name="Fuel", threshold_hours=6.0),
        projection,
    )

    assert alert is not None
    assert alert.kind == "projected_fuel_shortage"
    assert alert.resource_name == "Fuel"
    assert alert.hours_until_shortage == 4.0
    assert (
        alert.discord_message
        == "Fuel shortage projected in 4.0h. Resupply before operations stall."
    )


def test_evaluate_projected_shortage_alert_returns_none_when_threshold_is_not_met() -> None:
    projection = project_shortages(
        [
            ProjectionInput(name="Fuel", current_units=120, burn_rate_per_hour=30),
            ProjectionInput(name="Water Ice", current_units=500, burn_rate_per_hour=50),
        ]
    )

    alert = evaluate_projected_shortage_alert(
        AlertRule(resource_name="Fuel", threshold_hours=3.0),
        projection,
    )

    assert alert is None


def test_evaluate_projected_shortage_alert_returns_none_for_missing_resource_rule() -> None:
    projection = project_shortages(
        [
            ProjectionInput(name="Fuel", current_units=120, burn_rate_per_hour=30),
            ProjectionInput(name="Water Ice", current_units=500, burn_rate_per_hour=50),
        ]
    )

    alert = evaluate_projected_shortage_alert(
        AlertRule(resource_name="Heavy Water", threshold_hours=6.0),
        projection,
    )

    assert alert is None
