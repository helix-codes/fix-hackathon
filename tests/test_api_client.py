"""Public-interface tests for the resource dashboard data gateway.

These tests exercise the current offline-first client behavior through its
public methods. They act as the specification for deterministic mocked planner
data while live integration remains unimplemented.
"""

import json

from resource_dashboard.api_client import ApiClient


def test_fetch_resource_nodes_uses_fallback_data_when_offline() -> None:
    client = ApiClient(offline=True)

    nodes = client.fetch_resource_nodes()

    assert [node.id for node in nodes] == [
        "mock-asteroid-1",
        "mock-asteroid-2",
        "mock-asteroid-3",
    ]
    assert nodes[0].system == "K2-18"
    assert nodes[0].resource_type == "Titanium"
    assert nodes[0].freshness_hours == 2


def test_fetch_operational_snapshot_uses_mocked_planner_data_when_offline() -> None:
    client = ApiClient(offline=True)

    snapshot = client.fetch_operational_snapshot()

    assert snapshot.source.mode == "mocked"
    assert snapshot.source.label == "offline-fixture-pack"
    assert [node.id for node in snapshot.resource_nodes] == [
        "mock-asteroid-1",
        "mock-asteroid-2",
        "mock-asteroid-3",
    ]
    assert [base.id for base in snapshot.base_statuses] == ["mock-base-1"]
    assert snapshot.base_statuses[0].system == "K2-18"
    assert snapshot.base_statuses[0].fuel_units == 480


def test_fetch_pod_listings_uses_mocked_scan_intel_when_offline() -> None:
    client = ApiClient(offline=True)

    listings = client.fetch_pod_listings()

    assert [listing.preview().resource_class for listing in listings] == [
        "Titanium",
        "Water Ice",
    ]
    assert listings[0].preview().zone == "K2-18"
    assert listings[0].price_units == 250


def test_fetch_operational_snapshot_uses_localnet_artifacts_when_configured(
    tmp_path,
    monkeypatch,
) -> None:
    world_contracts = tmp_path / "world-contracts"
    deployments = world_contracts / "deployments" / "localnet"
    deployments.mkdir(parents=True)
    (world_contracts / ".env").write_text(
        "SUI_NETWORK=localnet\nTENANT=Stillness\n",
        encoding="utf-8",
    )
    (world_contracts / "test-resources.json").write_text(
        json.dumps(
            {
                "networkNode": {"typeId": 555, "itemId": 5550000012},
                "assembly": {"typeId": 87119, "itemId": 9999000005},
                "storageUnit": {"typeId": 88082, "itemId": 888800006},
                "gate": {"typeId": 88086, "itemId1": 90185, "itemId2": 90186},
            }
        ),
        encoding="utf-8",
    )
    (deployments / "extracted-object-ids.json").write_text(
        json.dumps(
            {
                "network": "localnet",
                "world": {
                    "packageId": "0xabc123",
                },
            }
        ),
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

    client = ApiClient(offline=False, localnet_root=str(tmp_path))

    snapshot = client.fetch_operational_snapshot()

    assert snapshot.source.mode == "localnet"
    assert snapshot.source.label == "Stillness:0xabc123"
    assert [node.resource_type for node in snapshot.resource_nodes] == [
        "Storage Unit",
        "Smart Gate",
        "Smart Gate",
        "Titanium",
        "Water Ice",
    ]
    assert [node.system for node in snapshot.resource_nodes] == [
        "Stillness",
        "Stillness",
        "Stillness",
        "Stillness",
        "Stillness",
    ]
    assert [base.id for base in snapshot.base_statuses] == ["0xnetwork-node"]
    assert snapshot.base_statuses[0].fuel_units == 250

    listings = client.fetch_pod_listings()

    assert [listing.preview().resource_class for listing in listings] == [
        "Titanium",
        "Water Ice",
    ]
    assert listings[0].preview().zone == "Stillness"
    assert listings[0].preview().approximate_richness == "High"
    assert (
        listings[0].intel.recommended_route
        == "Gate Alpha -> Storage Unit A -> Belt 3"
    )
