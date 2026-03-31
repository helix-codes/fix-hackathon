"""Public-interface tests for the wallet-backed POD purchase adapter.

These tests specify the minimal wallet and chain integration slice for the POD
purchase flow. The adapter should keep environment assumptions explicit and
leave the POD domain model isolated from wallet details.
"""

from resource_dashboard.pod_marketplace import ScanIntel, create_pod_listing
from resource_dashboard.wallet_purchase import PurchaseEnvironment, purchase_pod_with_wallet


def test_purchase_pod_with_wallet_returns_receipt_and_purchased_listing() -> None:
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

    receipt = purchase_pod_with_wallet(
        listing=listing,
        buyer_id="buyer-tribe-9",
        environment=PurchaseEnvironment(
            wallet_provider="EVE Vault",
            tenant="Utopia",
            network="testnet",
            settlement_asset="TEST_EVE",
        ),
        transaction_digest="0xabc123",
    )

    assert receipt.environment.wallet_provider == "EVE Vault"
    assert receipt.environment.tenant == "Utopia"
    assert receipt.environment.network == "testnet"
    assert receipt.environment.settlement_asset == "TEST_EVE"
    assert receipt.transaction_digest == "0xabc123"
    assert receipt.purchased_listing.buyer_id == "buyer-tribe-9"
    assert receipt.purchased_listing.reveal().exact_coordinates == "12.4,88.1"
