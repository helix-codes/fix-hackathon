"""Preflight checks for the localnet planner workflow.

This module verifies that the local Sui node, world-contracts artifacts, and
planner localnet snapshot path are healthy before live testing or a demo.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Final

from resource_dashboard.api_client import ApiClient
from resource_dashboard.demo import render_mocked_demo_dashboard
from resource_dashboard.localnet_demo import render_localnet_demo_dashboard

FRAME_WIDTH: Final[int] = 64
FRAME_RULE: Final[str] = "=" * FRAME_WIDTH
SECTION_RULE: Final[str] = "-" * FRAME_WIDTH
TITLE: Final[str] = "FIX // Localnet Preflight"
PREFLIGHT_EXCEPTIONS = (
    ConnectionError,
    FileNotFoundError,
    NotImplementedError,
    ValueError,
)


def run_localnet_preflight(localnet_root: str | None = None) -> str:
    """Runs the localnet planner preflight checks.

    Args:
        localnet_root: Workspace root containing `world-contracts/`.

    Returns:
        A human-readable summary of localnet readiness.
    """

    root = Path(localnet_root or Path.cwd())
    client = ApiClient(offline=False, localnet_root=str(root))
    snapshot = client.fetch_operational_snapshot()
    dashboard = render_localnet_demo_dashboard(str(root))

    return "\n".join(
        [
            FRAME_RULE,
            TITLE,
            SECTION_RULE,
            "Localnet Preflight: OK",
            f"Source Mode: {snapshot.source.mode}",
            f"Source Label: {snapshot.source.label}",
            f"Resource Count: {len(snapshot.resource_nodes)}",
            f"Base Count: {len(snapshot.base_statuses)}",
            (
                "Resource Types: "
                + (", ".join(sorted({node.resource_type for node in snapshot.resource_nodes})) or "None")
            ),
            f"Dashboard Rendered: {'Yes' if dashboard else 'No'}",
            FRAME_RULE,
        ]
    )


def run_localnet_preflight_with_mocked_fallback(
    localnet_root: str | None = None,
) -> str:
    """Runs the preflight with explicit mocked fallback reporting.

    Args:
        localnet_root: Workspace root containing `world-contracts/`.

    Returns:
        A failure summary when localnet is unavailable, optionally including the
        trusted mocked dashboard so operators can continue the demo. If the
        localnet checks succeed, returns the normal success summary.
    """

    try:
        return run_localnet_preflight(localnet_root)
    except PREFLIGHT_EXCEPTIONS as error:
        fallback_dashboard = render_mocked_demo_dashboard()
        return "\n".join(
            [
                FRAME_RULE,
                TITLE,
                SECTION_RULE,
                "Localnet Preflight: FAIL",
                f"Localnet Error: {error}",
                "Fallback Mode: mocked",
                "Fallback Dashboard Rendered: Yes",
                fallback_dashboard,
                FRAME_RULE,
            ]
        )


def main(argv: list[str] | None = None) -> None:
    """Prints the localnet planner preflight summary.

    Args:
        argv: Optional CLI arguments for testability.
    """

    parser = argparse.ArgumentParser(
        description="Verify localnet readiness for the planner workflow."
    )
    parser.add_argument(
        "--allow-mocked-fallback",
        action="store_true",
        help="Return the trusted mocked dashboard if localnet validation fails.",
    )
    arguments = parser.parse_args(argv)

    if arguments.allow_mocked_fallback:
        print(run_localnet_preflight_with_mocked_fallback())
        return

    print(run_localnet_preflight())


if __name__ == "__main__":
    main()
