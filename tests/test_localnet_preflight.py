"""Tests for the localnet planner preflight command."""

from resource_dashboard.localnet_preflight import (
    run_localnet_preflight,
    run_localnet_preflight_with_mocked_fallback,
)


def test_run_localnet_preflight_reports_snapshot_health(tmp_path, monkeypatch) -> None:
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
                {"label": "Titanium", "type_id": "120001"},
                {"label": "Water Ice", "type_id": "120002"},
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
                    "volume": "12",
                    "tenant": "Stillness",
                },
            ],
        },
    )

    summary = run_localnet_preflight(str(tmp_path))

    assert "FIX // Localnet Preflight" in summary
    assert "Localnet Preflight: OK" in summary
    assert "Source Mode: localnet" in summary
    assert "Resource Count: 5" in summary
    assert "Base Count: 1" in summary
    assert "Resource Types: Smart Gate, Storage Unit, Titanium, Water Ice" in summary
    assert "Dashboard Rendered: Yes" in summary


def test_run_localnet_preflight_with_mocked_fallback_reports_failure(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "resource_dashboard.api_client._fetch_localnet_snapshot_payload",
        lambda localnet_root, rpc_url="http://127.0.0.1:9000": (_ for _ in ()).throw(
            ConnectionError("RPC unavailable")
        ),
    )

    summary = run_localnet_preflight_with_mocked_fallback(str(tmp_path))

    assert "FIX // Localnet Preflight" in summary
    assert "Localnet Preflight: FAIL" in summary
    assert "Localnet Error: RPC unavailable" in summary
    assert "Fallback Mode: mocked" in summary
    assert "Fallback Dashboard Rendered: Yes" in summary
    assert "Data Source: MOCKED (offline-fixture-pack)" in summary
