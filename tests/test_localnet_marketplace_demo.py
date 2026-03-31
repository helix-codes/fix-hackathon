"""Public-interface tests for the localnet marketplace demo."""

from resource_dashboard.localnet_marketplace_demo import render_localnet_marketplace_demo


def test_render_localnet_marketplace_demo_shows_preview_and_reveal(
    tmp_path,
    monkeypatch,
) -> None:
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
                }
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
                }
            ],
        },
    )

    demo = render_localnet_marketplace_demo(str(tmp_path))

    assert "FIX // POD Intelligence Marketplace" in demo
    assert "Marketplace Source: LOCALNET" in demo
    assert "- Titanium in Stillness (High, 1h) for 250 units" in demo
    assert "Purchased POD: Titanium for 250 units" in demo
    assert "Reveal Coordinates: 12.4,88.1,3.2" in demo
    assert "Recommended Route: Gate Alpha -> Storage Unit A -> Belt 3" in demo
    assert "Settlement: EVE Vault on localnet" in demo
