"""Public-interface tests for the planner snapshot read model.

These tests define the first planner-facing filtering behavior that sits on top
of the offline data gateway. They intentionally work through public contracts
so the planner module can deepen without breaking the specification.
"""

from resource_dashboard.api_client import ApiClient
from resource_dashboard.planner_snapshot import PlannerFilters, build_planner_snapshot


def test_build_planner_snapshot_filters_gateway_data_for_planning_needs() -> None:
    client = ApiClient(offline=True)

    operational_snapshot = client.fetch_operational_snapshot()
    planner_snapshot = build_planner_snapshot(
        operational_snapshot,
        PlannerFilters(
            systems={"K2-18"},
            resource_types={"Titanium"},
            max_freshness_hours=6,
            operational_area_systems={"K2-18", "Jita"},
        ),
    )

    assert planner_snapshot.source.mode == "mocked"
    assert planner_snapshot.systems == ["K2-18"]
    assert planner_snapshot.resource_types == ["Titanium"]
    assert [node.id for node in planner_snapshot.resource_nodes] == ["mock-asteroid-1"]
    assert planner_snapshot.resource_nodes[0].freshness_hours == 2
