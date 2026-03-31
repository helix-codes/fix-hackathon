"""Localnet marketplace demo for POD-backed scan intelligence.

This module exercises the MVP intelligence-marketplace flow on top of the
localnet-seeded scan intel catalog: browse preview-safe listings, simulate a
fixed-price purchase, and reveal the premium payload after purchase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from resource_dashboard.api_client import ApiClient
from resource_dashboard.pod_marketplace import PodListing
from resource_dashboard.wallet_purchase import PurchaseEnvironment, purchase_pod_with_wallet

FRAME_WIDTH: Final[int] = 64
FRAME_RULE: Final[str] = "=" * FRAME_WIDTH
SECTION_RULE: Final[str] = "-" * FRAME_WIDTH
TITLE: Final[str] = "FIX // POD Intelligence Marketplace"
DEFAULT_BUYER_ID: Final[str] = "buyer-tribe-9"
SIMULATED_DIGEST: Final[str] = "localnet-simulated-digest"


def render_localnet_marketplace_demo(localnet_root: str | None = None) -> str:
    """Renders the localnet marketplace demo output.

    Args:
        localnet_root: Workspace root containing `world-contracts/`.

    Returns:
        A human-readable summary of listing previews and one purchased reveal.

    Raises:
        ValueError: No POD listings are available from localnet.
    """

    root = localnet_root or str(Path.cwd())
    client = ApiClient(offline=False, localnet_root=root)
    listings = client.fetch_pod_listings()
    if not listings:
        raise ValueError("No localnet POD listings are available.")

    chosen_listing = listings[0]
    preview_lines = [_render_preview_line(listing) for listing in listings]
    receipt = purchase_pod_with_wallet(
        listing=chosen_listing,
        buyer_id=DEFAULT_BUYER_ID,
        environment=_build_purchase_environment(),
        transaction_digest=SIMULATED_DIGEST,
    )
    reveal = receipt.purchased_listing.reveal()

    return "\n".join(
        [
            FRAME_RULE,
            TITLE,
            SECTION_RULE,
            "Marketplace Source: LOCALNET",
            "Available POD Listings:",
            *preview_lines,
            SECTION_RULE,
            (
                "Purchased POD: "
                f"{chosen_listing.preview().resource_class} "
                f"for {chosen_listing.price_units} units"
            ),
            f"Reveal Coordinates: {reveal.exact_coordinates}",
            f"Reveal Payload: {reveal.full_scan_payload}",
            f"Recommended Route: {reveal.recommended_route}",
            f"Settlement: {receipt.environment.wallet_provider} on {receipt.environment.network}",
            FRAME_RULE,
        ]
    )


def _render_preview_line(listing: PodListing) -> str:
    """Renders one preview-safe POD listing line."""

    preview = listing.preview()
    return (
        f"- {preview.resource_class} in {preview.zone} "
        f"({preview.approximate_richness}, {preview.freshness_hours}h) "
        f"for {listing.price_units} units"
    )


def _build_purchase_environment() -> PurchaseEnvironment:
    """Builds the explicit wallet assumptions for the MVP marketplace demo."""

    return PurchaseEnvironment(
        wallet_provider="EVE Vault",
        tenant="Stillness",
        network="localnet",
        settlement_asset="TEST_EVE",
    )


def main() -> None:
    """Prints the localnet marketplace demo."""

    print(render_localnet_marketplace_demo())


if __name__ == "__main__":
    main()
