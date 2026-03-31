"""Offline-first data gateway for planner-facing operational snapshots.

The current implementation keeps live integration out of the critical path by
returning deterministic mocked data when offline mode is enabled. Callers can
use the smaller endpoint methods directly or request a single operational
snapshot that carries both planner data and source metadata.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from resource_dashboard.pod_marketplace import PodListing, ScanIntel, create_pod_listing

DEFAULT_LOCALNET_RPC_URL: Final[str] = "http://127.0.0.1:9000"
LOCALNET_HELPER_SCRIPT: Final[Path] = Path(
    "world-contracts/ts-scripts/resource_dashboard/localnet-snapshot.ts"
)
LOCALNET_SOURCE_MODE: Final[str] = "localnet"
MOCKED_SOURCE_MODE: Final[str] = "mocked"
MOCKED_SOURCE_LABEL: Final[str] = "offline-fixture-pack"
Payload = dict[str, Any]


@dataclass(frozen=True)
class ResourceNode:
    """Represents a resource node visible to the planner.

    Attributes:
        id: Stable identifier for the resource node.
        system: The system or zone where the node is located.
        resource_type: The planner-facing resource class for the node.
        freshness_hours: Age of the scan intel expressed in hours.
    """

    id: str
    system: str
    resource_type: str
    freshness_hours: int


@dataclass(frozen=True)
class BaseStatus:
    """Represents the planner-visible status of a base.

    Attributes:
        id: Stable identifier for the base.
        system: The system or zone where the base is located.
        fuel_units: The mocked remaining fuel supply for the base.
    """

    id: str
    system: str
    fuel_units: int


@dataclass(frozen=True)
class SourceMetadata:
    """Describes where an operational snapshot came from.

    Attributes:
        mode: Whether the data is mocked or live.
        label: Human-readable identifier for the data source.
    """

    mode: str
    label: str


@dataclass(frozen=True)
class OperationalSnapshot:
    """Bundles planner-facing data with source metadata.

    Attributes:
        source: Metadata describing whether the data is mocked or live.
        resource_nodes: Resource nodes available to the planner.
        base_statuses: Base statuses available to the planner.
    """

    source: SourceMetadata
    resource_nodes: list[ResourceNode]
    base_statuses: list[BaseStatus]


class ApiClient:
    """Provides planner data through an offline-first interface."""

    def __init__(
        self,
        offline: bool = False,
        localnet_root: str | None = None,
        localnet_rpc_url: str = DEFAULT_LOCALNET_RPC_URL,
    ) -> None:
        """Initializes the client with the selected operating mode.

        Args:
            offline: Whether to use deterministic mocked data instead of live
                integrations.
            localnet_root: Workspace root containing the localnet tutorial repos.
            localnet_rpc_url: RPC endpoint used for localnet object verification.
        """

        self._offline = offline
        self._localnet_root = Path(localnet_root).resolve() if localnet_root else None
        self._localnet_rpc_url = localnet_rpc_url

    def _fetch_localnet_snapshot_payload(self) -> Payload:
        """Fetches the normalized localnet snapshot for the configured root."""

        assert self._localnet_root is not None
        return _fetch_localnet_snapshot_payload(
            self._localnet_root,
            rpc_url=self._localnet_rpc_url,
        )

    def fetch_resource_nodes(self) -> list[ResourceNode]:
        """Fetches resource nodes for the current operating mode.

        Returns:
            A deterministic list of planner-visible resource nodes.

        Raises:
            NotImplementedError: Live API support is not implemented yet.
        """

        if self._offline:
            return _mock_resource_nodes()

        if self._localnet_root is not None:
            return _build_localnet_resource_nodes(self._fetch_localnet_snapshot_payload())

        raise NotImplementedError("Live API support is not implemented yet.")

    def fetch_base_statuses(self) -> list[BaseStatus]:
        """Fetches base-status data for the current operating mode.

        Returns:
            A deterministic list of planner-visible base statuses.

        Raises:
            NotImplementedError: Live API support is not implemented yet.
        """

        if self._offline:
            return _mock_base_statuses()

        if self._localnet_root is not None:
            return _build_localnet_base_statuses(self._fetch_localnet_snapshot_payload())

        raise NotImplementedError("Live API support is not implemented yet.")

    def fetch_operational_snapshot(self) -> OperationalSnapshot:
        """Fetches a planner-ready operational snapshot.

        Returns:
            A snapshot containing source metadata, resource nodes, and base
            statuses for the current operating mode.

        Raises:
            NotImplementedError: Live API support is not implemented yet.
        """

        if self._offline:
            return OperationalSnapshot(
                source=SourceMetadata(
                    mode=MOCKED_SOURCE_MODE,
                    label=MOCKED_SOURCE_LABEL,
                ),
                resource_nodes=self.fetch_resource_nodes(),
                base_statuses=self.fetch_base_statuses(),
            )

        if self._localnet_root is not None:
            payload = self._fetch_localnet_snapshot_payload()
            return OperationalSnapshot(
                source=SourceMetadata(
                    mode=LOCALNET_SOURCE_MODE,
                    label=f"{payload['tenant']}:{payload['world_package_id'][:10]}",
                ),
                resource_nodes=_build_localnet_resource_nodes(payload),
                base_statuses=_build_localnet_base_statuses(payload),
            )

        raise NotImplementedError("Live API support is not implemented yet.")

    def fetch_pod_listings(self) -> list[PodListing]:
        """Fetches POD listings for the current operating mode.

        Returns:
            A deterministic set of fixed-price POD listings backed by either
            mocked fixtures or localnet-seeded scan intel.

        Raises:
            NotImplementedError: Live API support is not implemented yet.
        """

        if self._offline:
            return _mock_pod_listings()

        if self._localnet_root is not None:
            return _build_localnet_pod_listings(self._fetch_localnet_snapshot_payload())

        raise NotImplementedError("Live API support is not implemented yet.")


def _mock_resource_nodes() -> list[ResourceNode]:
    """Returns the deterministic mocked resource nodes."""

    return [
        ResourceNode(
            id="mock-asteroid-1",
            system="K2-18",
            resource_type="Titanium",
            freshness_hours=2,
        ),
        ResourceNode(
            id="mock-asteroid-2",
            system="K2-18",
            resource_type="Water Ice",
            freshness_hours=10,
        ),
        ResourceNode(
            id="mock-asteroid-3",
            system="Amarr",
            resource_type="Titanium",
            freshness_hours=1,
        ),
    ]


def _mock_base_statuses() -> list[BaseStatus]:
    """Returns the deterministic mocked base statuses."""

    return [
        BaseStatus(
            id="mock-base-1",
            system="K2-18",
            fuel_units=480,
        )
    ]


def _mock_pod_listings() -> list[PodListing]:
    """Returns deterministic mocked POD listings for the marketplace MVP."""

    return [
        create_pod_listing(
            seller_id="scout-tribe-1",
            price_units=250,
            intel=ScanIntel(
                zone="K2-18",
                resource_class="Titanium",
                approximate_richness="High",
                freshness_hours=2,
                exact_coordinates="12.4,88.1,3.2",
                full_scan_payload="vein-density=0.91;cluster=7;extractor=ore",
                recommended_route="Gate A -> Belt 3 -> Safe Dock",
            ),
        ),
        create_pod_listing(
            seller_id="scout-tribe-2",
            price_units=275,
            intel=ScanIntel(
                zone="K2-18",
                resource_class="Water Ice",
                approximate_richness="Medium",
                freshness_hours=3,
                exact_coordinates="14.0,74.5,9.1",
                full_scan_payload="vein-density=0.76;cluster=3;extractor=ice",
                recommended_route="Gate B -> Ice Ring 2 -> Safe Dock",
            ),
        ),
    ]


def _fetch_localnet_snapshot_payload(
    localnet_root: Path,
    rpc_url: str = DEFAULT_LOCALNET_RPC_URL,
) -> Payload:
    """Fetches a real localnet structure snapshot through world-contracts.

    Args:
        localnet_root: Workspace root containing the tutorial repos.
        rpc_url: Localnet JSON-RPC endpoint.

    Returns:
        A localnet structure snapshot payload returned by the helper script.

    Raises:
        FileNotFoundError: The localnet helper script is missing.
        ConnectionError: The helper script fails or returns invalid JSON.
    """

    helper_path = localnet_root / LOCALNET_HELPER_SCRIPT
    if not helper_path.exists():
        raise FileNotFoundError(f"Required localnet helper script is missing: {helper_path}")

    environment = os.environ.copy()
    environment["SUI_NETWORK"] = "localnet"
    environment.setdefault("SUI_RPC_URL", rpc_url)

    result = subprocess.run(
        [
            "pnpm",
            "exec",
            "tsx",
            "ts-scripts/resource_dashboard/localnet-snapshot.ts",
        ],
        cwd=localnet_root / "world-contracts",
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ConnectionError(
            "Failed to fetch localnet snapshot from world-contracts: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ConnectionError("Localnet snapshot helper returned invalid JSON.") from error

    if not isinstance(payload, dict):
        raise ConnectionError("Localnet snapshot helper did not return an object.")

    return payload


def _build_localnet_resource_nodes(payload: Payload) -> list[ResourceNode]:
    """Builds planner-facing resource nodes from real localnet object reads."""

    tenant = str(payload["tenant"])
    connected_structures = _require_list(payload, "connected_structures")
    inventory_entries = _require_list(payload, "storage_inventory_entries")
    planner_resource_catalog = _require_list(payload, "planner_resource_catalog")

    resource_labels_by_type = {
        str(entry["type_id"]): str(entry["label"])
        for entry in planner_resource_catalog
        if isinstance(entry, dict)
        and "type_id" in entry
        and "label" in entry
    }

    resource_nodes = [
        ResourceNode(
            id=str(structure["object_id"]),
            system=tenant,
            resource_type=_planner_resource_type_for_structure(structure),
            freshness_hours=0,
        )
        for structure in connected_structures
        if isinstance(structure, dict)
    ]
    resource_nodes.extend(
        [
            ResourceNode(
                id=(
                    f"{entry['inventory_key']}::{entry['type_id']}::"
                    f"{entry['item_id']}::{entry['inventory_kind']}"
                ),
                system=tenant,
                resource_type=_planner_resource_type_for_inventory_entry(
                    {
                        **entry,
                        "_planner_resource_catalog": resource_labels_by_type,
                    }
                ),
                freshness_hours=0,
            )
            for entry in inventory_entries
            if isinstance(entry, dict)
            and str(entry.get("type_id")) in resource_labels_by_type
        ]
    )
    return resource_nodes


def _build_localnet_base_statuses(payload: Payload) -> list[BaseStatus]:
    """Builds planner-facing base statuses from real localnet object reads."""

    tenant = str(payload["tenant"])
    network_node = payload.get("network_node", {})
    if not isinstance(network_node, dict):
        raise ValueError("Localnet snapshot payload is missing network_node.")

    return [
        BaseStatus(
            id=str(network_node["object_id"]),
            system=tenant,
            fuel_units=int(network_node.get("fuel_quantity") or 0),
        )
    ]


def _build_localnet_pod_listings(payload: Payload) -> list[PodListing]:
    """Builds POD listings from localnet-seeded scan-intel metadata."""

    tenant = str(payload["tenant"])
    inventory_entries = _require_list(payload, "storage_inventory_entries")
    planner_resource_catalog = _require_list(payload, "planner_resource_catalog")

    present_type_ids = {
        str(entry.get("type_id"))
        for entry in inventory_entries
        if isinstance(entry, dict)
    }

    listings: list[PodListing] = []
    for entry in planner_resource_catalog:
        if not isinstance(entry, dict):
            continue
        type_id = str(entry.get("type_id"))
        if type_id not in present_type_ids:
            continue
        listings.append(
            create_pod_listing(
                seller_id="localnet-scout",
                price_units=int(entry.get("price_units") or 250),
                intel=ScanIntel(
                    zone=tenant,
                    resource_class=str(entry.get("label") or f"Item Type {type_id}"),
                    approximate_richness=str(
                        entry.get("approximate_richness") or "Medium"
                    ),
                    freshness_hours=int(entry.get("freshness_hours") or 1),
                    exact_coordinates=str(
                        entry.get("exact_coordinates") or "0.0,0.0,0.0"
                    ),
                    full_scan_payload=str(
                        entry.get("full_scan_payload") or "vein-density=unknown"
                    ),
                    recommended_route=str(
                        entry.get("recommended_route") or "Gate Alpha -> Target Site"
                    ),
                ),
            )
        )
    return listings


def _planner_resource_type_for_structure(structure: dict[str, object]) -> str:
    """Maps a localnet structure kind to a planner-facing resource label."""

    kind = structure.get("kind")
    if kind == "storage_unit":
        return "Storage Unit"
    if kind == "gate":
        return "Smart Gate"
    if kind == "turret":
        return "Turret"
    return "Assembly"


def _planner_resource_type_for_inventory_entry(entry: dict[str, object]) -> str:
    """Maps a live inventory entry to a planner-facing resource label."""

    type_id = str(entry.get("type_id"))
    catalog = entry.get("_planner_resource_catalog")
    if isinstance(catalog, dict):
        label = catalog.get(type_id)
        if isinstance(label, str):
            return label
    return f"Item Type {type_id}"


def _require_list(payload: Payload, field_name: str) -> list[Any]:
    """Returns a required list field from the localnet payload.

    Args:
        payload: The normalized localnet payload.
        field_name: The field expected to contain a list.

    Returns:
        The requested list value.

    Raises:
        ValueError: The field is missing or not a list.
    """

    value = payload.get(field_name)
    if not isinstance(value, list):
        raise ValueError(f"Localnet snapshot payload is missing {field_name}.")
    return value
