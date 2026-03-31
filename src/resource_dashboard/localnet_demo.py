"""Localnet smoke entrypoint for the planner workflow.

This module exercises the current planner shell against the localnet tutorial
artifacts and the running local Sui RPC. It is intentionally narrower than the
mocked demo and exists to prove the first live/localnet read seam.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Final

from resource_dashboard.dashboard_shell import DashboardRequest, render_dashboard_shell
from resource_dashboard.demo import render_mocked_demo_dashboard

LOCALNET_SYSTEMS: Final[set[str]] = {"Stillness"}
LOCALNET_GOAL_NAME: Final[str] = "Localnet Resource Readiness"
LOCALNET_GOAL_RESOURCE_TYPES: Final[set[str]] = {
    "Storage Unit",
    "Smart Gate",
    "Titanium",
    "Water Ice",
}
LOCALNET_PROJECTION_INPUTS: Final[list[tuple[str, float, float]]] = [
    ("Fuel", 1, 0.125),
    ("Gate Capacity", 10, 2),
]
LOCALNET_DEMO_EXCEPTIONS = (
    ConnectionError,
    FileNotFoundError,
    NotImplementedError,
    ValueError,
)


def render_localnet_demo_dashboard(localnet_root: str | None = None) -> str:
    """Renders the localnet planner smoke dashboard.

    Args:
        localnet_root: Workspace root containing `world-contracts/`.

    Returns:
        A dashboard-style summary sourced from localnet deployment artifacts.
    """

    root = localnet_root or str(Path.cwd())
    return render_dashboard_shell(
        DashboardRequest(
            systems=LOCALNET_SYSTEMS,
            operational_area_systems=LOCALNET_SYSTEMS,
            max_freshness_hours=1,
            goal_name=LOCALNET_GOAL_NAME,
            goal_resource_types=LOCALNET_GOAL_RESOURCE_TYPES,
            projection_inputs=LOCALNET_PROJECTION_INPUTS,
            alert_resource_name="Fuel",
            alert_threshold_hours=10.0,
            data_source_mode="localnet",
            localnet_root=root,
        )
    )


def render_localnet_demo_with_mocked_fallback(
    localnet_root: str | None = None,
) -> str:
    """Renders the localnet dashboard with an explicit mocked fallback.

    Args:
        localnet_root: Workspace root containing `world-contracts/`.

    Returns:
        The localnet dashboard when available. If the live/localnet path fails,
        returns a clearly labeled mocked fallback dashboard with the failure
        reason included for operators.
    """

    try:
        return render_localnet_demo_dashboard(localnet_root)
    except LOCALNET_DEMO_EXCEPTIONS as error:
        return "\n".join(
            [
                "Localnet Demo: MOCKED FALLBACK",
                f"Localnet Error: {error}",
                render_mocked_demo_dashboard(),
            ]
        )


def main(argv: list[str] | None = None) -> None:
    """Prints the localnet planner smoke dashboard.

    Args:
        argv: Optional CLI arguments for testability.
    """

    parser = argparse.ArgumentParser(
        description="Render the planner dashboard from localnet or mocked data."
    )
    parser.add_argument(
        "--fallback-to-mocked",
        action="store_true",
        help="Render the trusted mocked demo if the localnet path fails.",
    )
    arguments = parser.parse_args(argv)

    if arguments.fallback_to_mocked:
        print(render_localnet_demo_with_mocked_fallback())
        return

    print(render_localnet_demo_dashboard())


if __name__ == "__main__":
    main()
