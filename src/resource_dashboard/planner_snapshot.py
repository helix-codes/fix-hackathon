"""Planner-facing read model and filtering logic.

This module turns an operational snapshot from the gateway into a planner-ready
view that can be consumed by later UI or planning logic without knowing how the
underlying data was fetched.
"""

from dataclasses import dataclass

from resource_dashboard.api_client import OperationalSnapshot, ResourceNode, SourceMetadata


@dataclass(frozen=True)
class PlannerFilters:
    """Defines planner-facing filter criteria.

    Attributes:
        systems: Systems or zones to include.
        resource_types: Resource classes to include.
        max_freshness_hours: Maximum allowed age for scan intel.
        operational_area_systems: Systems considered inside the active planning
            area.
    """

    systems: set[str]
    resource_types: set[str]
    max_freshness_hours: int | None
    operational_area_systems: set[str]


@dataclass(frozen=True)
class PlannerSnapshot:
    """Represents a filtered planner-facing operational view.

    Attributes:
        source: Source metadata inherited from the gateway snapshot.
        systems: Sorted systems represented in the filtered result.
        resource_types: Sorted resource classes represented in the filtered
            result.
        resource_nodes: Filtered planner-visible resource nodes.
    """

    source: SourceMetadata
    systems: list[str]
    resource_types: list[str]
    resource_nodes: list[ResourceNode]


def build_planner_snapshot(
    operational_snapshot: OperationalSnapshot,
    filters: PlannerFilters,
) -> PlannerSnapshot:
    """Builds a planner-facing snapshot from gateway data.

    Args:
        operational_snapshot: The gateway snapshot to filter.
        filters: Planner-facing filtering rules.

    Returns:
        A filtered planner snapshot that preserves the original source metadata.
    """

    resource_nodes = [
        node
        for node in operational_snapshot.resource_nodes
        if _matches_filters(node, filters)
    ]

    return PlannerSnapshot(
        source=operational_snapshot.source,
        systems=sorted({node.system for node in resource_nodes}),
        resource_types=sorted({node.resource_type for node in resource_nodes}),
        resource_nodes=resource_nodes,
    )


def _matches_filters(node: ResourceNode, filters: PlannerFilters) -> bool:
    """Checks whether a resource node should be included in the planner view."""

    if filters.operational_area_systems and node.system not in filters.operational_area_systems:
        return False

    if filters.systems and node.system not in filters.systems:
        return False

    if filters.resource_types and node.resource_type not in filters.resource_types:
        return False

    if (
        filters.max_freshness_hours is not None
        and node.freshness_hours > filters.max_freshness_hours
    ):
        return False

    return True
