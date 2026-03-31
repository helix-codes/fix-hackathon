"""Public-interface tests for the localnet smoke dashboard.

These tests verify that the first localnet planner shell can render from
localnet artifacts without disturbing the trusted mocked demo path.
"""

from resource_dashboard.localnet_demo import (
    render_localnet_demo_dashboard,
    render_localnet_demo_with_mocked_fallback,
)


def test_render_localnet_demo_dashboard_uses_localnet_mode(tmp_path, monkeypatch) -> None:
    world_contracts = tmp_path / "world-contracts"
    deployments = world_contracts / "deployments" / "localnet"
    deployments.mkdir(parents=True)
    (world_contracts / ".env").write_text(
        "SUI_NETWORK=localnet\nTENANT=Stillness\n",
        encoding="utf-8",
    )
    (world_contracts / "test-resources.json").write_text(
        """
        {
          "networkNode": {"typeId": 555, "itemId": 5550000012},
          "assembly": {"typeId": 87119, "itemId": 9999000005},
          "storageUnit": {"typeId": 88082, "itemId": 888800006},
          "gate": {"typeId": 88086, "itemId1": 90185, "itemId2": 90186}
        }
        """.strip(),
        encoding="utf-8",
    )
    (deployments / "extracted-object-ids.json").write_text(
        """
        {
          "network": "localnet",
          "world": {"packageId": "0xabc123"}
        }
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "resource_dashboard.api_client._fetch_localnet_snapshot_payload",
        lambda localnet_root, rpc_url="http://127.0.0.1:9000": {
            "tenant": "Stillness",
            "world_package_id": "0xabc123",
            "network_node": {
                "object_id": "0xnetwork-node",
                "fuel_quantity": 250,
                "is_online": True,
            },
            "connected_structures": [
                {"object_id": "0xstorage", "kind": "storage_unit"},
                {"object_id": "0xgate-1", "kind": "gate"},
                {"object_id": "0xgate-2", "kind": "gate"},
            ],
            "planner_resource_catalog": [
                {
                    "label": "Titanium",
                    "type_id": "120001",
                    "approximate_richness": "High",
                    "freshness_hours": 1,
                    "exact_coordinates": "12.4,88.1,3.2",
                    "full_scan_payload": "vein-density=0.91;cluster=7;extractor=ore",
                    "recommended_route": "Gate Alpha -> Storage Unit A -> Belt 3",
                    "price_units": 250,
                },
                {
                    "label": "Water Ice",
                    "type_id": "120002",
                    "approximate_richness": "Medium",
                    "freshness_hours": 1,
                    "exact_coordinates": "14.0,74.5,9.1",
                    "full_scan_payload": "vein-density=0.76;cluster=3;extractor=ice",
                    "recommended_route": "Gate Beta -> Ice Ring 2 -> Storage Unit A",
                    "price_units": 275,
                },
            ],
            "storage_inventory_entries": [
                {
                    "inventory_key": "0xowner",
                    "inventory_kind": "storage_owner",
                    "type_id": "120001",
                    "item_id": "120001001",
                    "quantity": 40,
                    "volume": "10",
                    "tenant": "Stillness",
                },
                {
                    "inventory_key": "0xowner",
                    "inventory_kind": "storage_owner",
                    "type_id": "120002",
                    "item_id": "120002001",
                    "quantity": 60,
                    "volume": "10",
                    "tenant": "Stillness",
                }
            ],
        },
    )

    dashboard = render_localnet_demo_dashboard(str(tmp_path))

    assert "FIX // Frontier Intel Exchange" in dashboard
    assert "Data Source: LOCALNET (Stillness:0xabc123)" in dashboard
    assert "Systems In View: Stillness" in dashboard
    assert "Resources In View: Smart Gate, Storage Unit, Titanium, Water Ice" in dashboard
    assert "Goal: Localnet Resource Readiness" in dashboard
    assert "Feasibility: FEASIBLE" in dashboard
    assert (
        "Intel Marketplace: Titanium (High, 1h, 250 units); "
        "Water Ice (Medium, 1h, 275 units)"
    ) in dashboard


def test_render_localnet_demo_with_mocked_fallback_reports_localnet_failure(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "resource_dashboard.api_client._fetch_localnet_snapshot_payload",
        lambda localnet_root, rpc_url="http://127.0.0.1:9000": (_ for _ in ()).throw(
            ConnectionError("RPC unavailable")
        ),
    )

    dashboard = render_localnet_demo_with_mocked_fallback(str(tmp_path))

    assert "Localnet Demo: MOCKED FALLBACK" in dashboard
    assert "Localnet Error: RPC unavailable" in dashboard
    assert "FIX // Frontier Intel Exchange" in dashboard
    assert "Data Source: MOCKED (offline-fixture-pack)" in dashboard
