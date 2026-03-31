"""Public-interface tests for the first dashboard shell.

These tests specify a minimal presentation shell for the current planner
workflow. The shell should present the key planning outputs in one coherent
view without depending on any frontend framework.
"""

from resource_dashboard.dashboard_shell import DashboardRequest, render_dashboard_shell


def test_render_dashboard_shell_presents_the_planner_story_in_one_view() -> None:
    dashboard = render_dashboard_shell(
        DashboardRequest(
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

    assert "FIX // Frontier Intel Exchange" in dashboard
    assert "Data Source: MOCKED (offline-fixture-pack)" in dashboard
    assert "Systems In View: K2-18" in dashboard
    assert "Resources In View: Titanium, Water Ice" in dashboard
    assert "Goal: Sustained Alloy Batch" in dashboard
    assert "Feasibility: FEASIBLE" in dashboard
    assert (
        "Intel Marketplace: Titanium (High, 2h, 250 units); "
        "Water Ice (Medium, 3h, 275 units)"
    ) in dashboard
    assert "First Bottleneck: Fuel in 4.0h" in dashboard
    assert "Alert: Fuel shortage projected in 4.0h. Resupply before operations stall." in dashboard
