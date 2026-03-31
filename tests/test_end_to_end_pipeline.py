"""End-to-end integration tests for the current planner workflow.

These tests exercise the implemented pipeline from mocked data ingestion
through planner filtering, feasibility evaluation, shortage projection, and
alert rendering.
"""

from resource_dashboard.pipeline import PipelineRequest, run_planner_pipeline


def test_run_planner_pipeline_exercises_the_current_mocked_demo_story() -> None:
    result = run_planner_pipeline(
        PipelineRequest(
            systems={"K2-18"},
            operational_area_systems={"K2-18"},
            max_freshness_hours=12,
            goal_name="Sustained Alloy Batch",
            goal_resource_types={"Titanium", "Water Ice"},
            projection_inputs=[
                ("Fuel", 120, 30),
                ("Water Ice", 500, 50),
            ],
            alert_resource_name="Fuel",
            alert_threshold_hours=6.0,
        )
    )

    assert result.snapshot.source.mode == "mocked"
    assert [node.id for node in result.snapshot.resource_nodes] == [
        "mock-asteroid-1",
        "mock-asteroid-2",
    ]
    assert result.feasibility.goal_name == "Sustained Alloy Batch"
    assert result.feasibility.is_feasible is True
    assert result.feasibility.missing_resource_types == []
    assert [listing.preview().resource_class for listing in result.pod_listings] == [
        "Titanium",
        "Water Ice",
    ]
    assert result.projection.first_bottleneck_name == "Fuel"
    assert result.projection.first_bottleneck_hours == 4.0
    assert result.alert is not None
    assert (
        result.alert.discord_message
        == "Fuel shortage projected in 4.0h. Resupply before operations stall."
    )
