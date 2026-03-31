"""Public-interface tests for the mocked demo entrypoint.

These tests verify that the trusted operator-facing demo path produces the
expected planner story from deterministic mocked data.
"""

from resource_dashboard.demo import render_mocked_demo_dashboard


def test_render_mocked_demo_dashboard_shows_the_submission_story() -> None:
    dashboard = render_mocked_demo_dashboard()

    assert "Data Source: MOCKED (offline-fixture-pack)" in dashboard
    assert "Goal: Sustained Alloy Batch" in dashboard
    assert "Feasibility: FEASIBLE" in dashboard
    assert "First Bottleneck: Fuel in 4.0h" in dashboard
    assert "Alert: Fuel shortage projected in 4.0h. Resupply before operations stall." in dashboard
