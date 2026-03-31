"""Public-interface tests for operational shortage projections.

These tests specify the first deterministic projection behavior for fuel and
critical-resource shortages. The projection engine should report time to
shortage and identify which tracked constraint fails first.
"""

import pytest

from resource_dashboard.projection import ProjectionInput, project_shortages


def test_project_shortages_identifies_time_to_shortage_and_first_bottleneck() -> None:
    projection = project_shortages(
        [
            ProjectionInput(name="Fuel", current_units=120, burn_rate_per_hour=30),
            ProjectionInput(name="Water Ice", current_units=500, burn_rate_per_hour=50),
        ]
    )

    assert projection.first_bottleneck_name == "Fuel"
    assert projection.first_bottleneck_hours == 4.0
    assert projection.entries[0].name == "Fuel"
    assert projection.entries[0].hours_until_shortage == 4.0
    assert projection.entries[1].name == "Water Ice"
    assert projection.entries[1].hours_until_shortage == 10.0


def test_project_shortages_rejects_empty_inputs() -> None:
    with pytest.raises(ValueError, match="At least one projection input is required."):
        project_shortages([])


def test_project_shortages_rejects_non_positive_burn_rates() -> None:
    with pytest.raises(
        ValueError,
        match="Burn rate must be positive for all projection inputs.",
    ):
        project_shortages(
            [
                ProjectionInput(name="Fuel", current_units=120, burn_rate_per_hour=0),
                ProjectionInput(
                    name="Water Ice",
                    current_units=500,
                    burn_rate_per_hour=50,
                ),
            ]
        )
