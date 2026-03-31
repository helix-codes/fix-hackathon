"""POD listing domain with explicit preview and reveal boundaries.

This module models the smallest credible POD marketplace contract for the
hackathon: create a fixed-price listing, expose preview-safe metadata before
purchase, and reveal premium intel only after purchase.
"""

from __future__ import annotations

from dataclasses import dataclass

PRE_PURCHASE_REVEAL_ERROR = "Cannot reveal premium intel before purchase."
DOUBLE_PURCHASE_ERROR = "POD listing has already been purchased."


@dataclass(frozen=True)
class ScanIntel:
    """Represents the full premium scan-intel package.

    Attributes:
        zone: Public zone identifier.
        resource_class: Public planner-facing resource class.
        approximate_richness: Public richness estimate safe for preview.
        freshness_hours: Public freshness indicator in hours.
        exact_coordinates: Premium exact coordinates revealed after purchase.
        full_scan_payload: Premium full scan payload revealed after purchase.
        recommended_route: Premium recommended extraction route revealed after
            purchase.
    """

    zone: str
    resource_class: str
    approximate_richness: str
    freshness_hours: int
    exact_coordinates: str
    full_scan_payload: str
    recommended_route: str


@dataclass(frozen=True)
class PodPreview:
    """Represents the pre-purchase metadata visible to all buyers.

    Attributes:
        zone: Public zone identifier.
        resource_class: Public planner-facing resource class.
        approximate_richness: Public richness estimate.
        freshness_hours: Public freshness indicator in hours.
    """

    zone: str
    resource_class: str
    approximate_richness: str
    freshness_hours: int


@dataclass(frozen=True)
class PodReveal:
    """Represents the premium intel revealed after purchase.

    Attributes:
        exact_coordinates: Premium exact coordinates.
        full_scan_payload: Premium scan payload.
        recommended_route: Premium recommended extraction route.
    """

    exact_coordinates: str
    full_scan_payload: str
    recommended_route: str


@dataclass(frozen=True)
class PodListing:
    """Represents a fixed-price POD listing.

    Attributes:
        seller_id: Seller identifier for the listing.
        price_units: Fixed sale price in application-level units.
        intel: Full premium intel associated with the listing.
        buyer_id: Buyer identifier after purchase, if any.
    """

    seller_id: str
    price_units: int
    intel: ScanIntel
    buyer_id: str | None = None

    def preview(self) -> PodPreview:
        """Builds the preview-safe metadata for the listing."""

        return PodPreview(
            zone=self.intel.zone,
            resource_class=self.intel.resource_class,
            approximate_richness=self.intel.approximate_richness,
            freshness_hours=self.intel.freshness_hours,
        )

    def reveal(self) -> PodReveal:
        """Returns the premium intel only when the listing is purchased.

        Raises:
            ValueError: The listing has not been purchased yet.
        """

        if self.buyer_id is None:
            raise ValueError(PRE_PURCHASE_REVEAL_ERROR)

        return PodReveal(
            exact_coordinates=self.intel.exact_coordinates,
            full_scan_payload=self.intel.full_scan_payload,
            recommended_route=self.intel.recommended_route,
        )


def create_pod_listing(
    seller_id: str,
    price_units: int,
    intel: ScanIntel,
) -> PodListing:
    """Creates a fixed-price POD listing from scan intel."""

    return PodListing(
        seller_id=seller_id,
        price_units=price_units,
        intel=intel,
    )


def purchase_pod_listing(listing: PodListing, buyer_id: str) -> PodListing:
    """Marks a POD listing as purchased by the given buyer.

    Raises:
        ValueError: The listing has already been purchased.
    """

    if listing.buyer_id is not None:
        raise ValueError(DOUBLE_PURCHASE_ERROR)

    return PodListing(
        seller_id=listing.seller_id,
        price_units=listing.price_units,
        intel=listing.intel,
        buyer_id=buyer_id,
    )


def filter_pod_listings(
    listings: list[PodListing],
    resource_classes: set[str],
    max_freshness_hours: int | None = None,
) -> list[PodListing]:
    """Filters POD listings by public preview metadata.

    Args:
        listings: Listings to evaluate.
        resource_classes: Resource classes relevant to the current goal.
        max_freshness_hours: Optional freshness threshold for preview intel.

    Returns:
        The listings whose public preview metadata matches the requested
        resource classes and freshness constraints.
    """

    return [
        listing
        for listing in listings
        if _matches_listing_filters(
            listing,
            resource_classes=resource_classes,
            max_freshness_hours=max_freshness_hours,
        )
    ]


def _matches_listing_filters(
    listing: PodListing,
    resource_classes: set[str],
    max_freshness_hours: int | None,
) -> bool:
    """Checks whether a listing matches the current preview filters."""

    preview = listing.preview()
    if resource_classes and preview.resource_class not in resource_classes:
        return False
    if max_freshness_hours is not None and preview.freshness_hours > max_freshness_hours:
        return False
    return True
