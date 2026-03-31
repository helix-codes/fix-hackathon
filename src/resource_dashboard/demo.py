"""Mocked planner demo entrypoint for hackathon submissions.

This module exposes one trusted, operator-facing command that renders the
current planner story from deterministic mocked data. It is intentionally small
so the demo path stays stable even when optional integrations remain unresolved.
"""

from resource_dashboard.dashboard_shell import DashboardRequest, render_dashboard_shell


def render_mocked_demo_dashboard() -> str:
    """Renders the trusted mocked planner demo output.

    Returns:
        A single dashboard-style text view for the current hackathon demo path.
    """

    return render_dashboard_shell(
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


def main() -> None:
    """Prints the trusted mocked planner demo output."""

    print(render_mocked_demo_dashboard())


if __name__ == "__main__":
    main()
