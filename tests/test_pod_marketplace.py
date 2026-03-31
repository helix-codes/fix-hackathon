"""Public-interface tests for the POD marketplace domain.

These tests specify the first POD listing contract: preview-safe metadata
before purchase, premium reveal after purchase, and a fixed-price sale path.
"""

import pytest

from resource_dashboard.pod_marketplace import (
    ScanIntel,
    create_pod_listing,
    filter_pod_listings,
    purchase_pod_listing,
)


def test_pod_listing_preserves_preview_boundary_and_reveals_after_purchase() -> None:
    listing = create_pod_listing(
        seller_id="seller-tribe-1",
        price_units=250,
        intel=ScanIntel(
            zone="K2-18",
            resource_class="Titanium",
            approximate_richness="High",
            freshness_hours=2,
            exact_coordinates="12.4,88.1",
            full_scan_payload="vein-density=0.91;cluster=7",
            recommended_route="Gate A -> Belt 3 -> Safe Dock",
        ),
    )

    preview = listing.preview()
    purchased = purchase_pod_listing(listing, buyer_id="buyer-tribe-9")
    reveal = purchased.reveal()

    assert preview.zone == "K2-18"
    assert preview.resource_class == "Titanium"
    assert preview.approximate_richness == "High"
    assert preview.freshness_hours == 2
    assert purchased.price_units == 250
    assert purchased.buyer_id == "buyer-tribe-9"
    assert reveal.exact_coordinates == "12.4,88.1"
    assert reveal.full_scan_payload == "vein-density=0.91;cluster=7"
    assert reveal.recommended_route == "Gate A -> Belt 3 -> Safe Dock"


def test_pod_listing_rejects_reveal_before_purchase() -> None:
    listing = create_pod_listing(
        seller_id="seller-tribe-1",
        price_units=250,
        intel=ScanIntel(
            zone="K2-18",
            resource_class="Titanium",
            approximate_richness="High",
            freshness_hours=2,
            exact_coordinates="12.4,88.1",
            full_scan_payload="vein-density=0.91;cluster=7",
            recommended_route="Gate A -> Belt 3 -> Safe Dock",
        ),
    )

    with pytest.raises(ValueError, match="Cannot reveal premium intel before purchase."):
        listing.reveal()


def test_pod_listing_rejects_double_purchase() -> None:
    listing = create_pod_listing(
        seller_id="seller-tribe-1",
        price_units=250,
        intel=ScanIntel(
            zone="K2-18",
            resource_class="Titanium",
            approximate_richness="High",
            freshness_hours=2,
            exact_coordinates="12.4,88.1",
            full_scan_payload="vein-density=0.91;cluster=7",
            recommended_route="Gate A -> Belt 3 -> Safe Dock",
        ),
    )
    purchased = purchase_pod_listing(listing, buyer_id="buyer-tribe-9")

    with pytest.raises(ValueError, match="POD listing has already been purchased."):
        purchase_pod_listing(purchased, buyer_id="buyer-tribe-10")


def test_filter_pod_listings_uses_preview_metadata() -> None:
    listings = [
        create_pod_listing(
            seller_id="seller-tribe-1",
            price_units=250,
            intel=ScanIntel(
                zone="K2-18",
                resource_class="Titanium",
                approximate_richness="High",
                freshness_hours=2,
                exact_coordinates="12.4,88.1",
                full_scan_payload="vein-density=0.91;cluster=7",
                recommended_route="Gate A -> Belt 3 -> Safe Dock",
            ),
        ),
        create_pod_listing(
            seller_id="seller-tribe-2",
            price_units=275,
            intel=ScanIntel(
                zone="K2-18",
                resource_class="Water Ice",
                approximate_richness="Medium",
                freshness_hours=14,
                exact_coordinates="14.0,74.5",
                full_scan_payload="vein-density=0.76;cluster=3",
                recommended_route="Gate B -> Ring 2 -> Safe Dock",
            ),
        ),
    ]

    filtered = filter_pod_listings(
        listings,
        resource_classes={"Titanium", "Water Ice"},
        max_freshness_hours=6,
    )

    assert [listing.preview().resource_class for listing in filtered] == ["Titanium"]
