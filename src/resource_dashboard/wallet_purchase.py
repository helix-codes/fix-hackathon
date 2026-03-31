"""Thin wallet-and-chain purchase adapter for POD listings.

This module keeps wallet and chain environment assumptions explicit while
delegating listing state changes to the POD marketplace domain. It provides the
smallest credible seam for a future EVE Vault and transaction-backed purchase
flow.
"""

from dataclasses import dataclass

from resource_dashboard.pod_marketplace import PodListing, purchase_pod_listing


@dataclass(frozen=True)
class PurchaseEnvironment:
    """Describes the wallet and chain assumptions for a POD purchase.

    Attributes:
        wallet_provider: Wallet provider expected by the purchase flow.
        tenant: EVE Frontier tenant used for the demo environment.
        network: Target chain network for the purchase flow.
        settlement_asset: Asset used for fixed-price settlement.
    """

    wallet_provider: str
    tenant: str
    network: str
    settlement_asset: str


@dataclass(frozen=True)
class PurchaseReceipt:
    """Represents the result of a wallet-backed POD purchase.

    Attributes:
        environment: Wallet and chain assumptions used for the purchase.
        transaction_digest: Recorded transaction or simulated transaction id.
        purchased_listing: POD listing state after purchase.
    """

    environment: PurchaseEnvironment
    transaction_digest: str
    purchased_listing: PodListing


def purchase_pod_with_wallet(
    listing: PodListing,
    buyer_id: str,
    environment: PurchaseEnvironment,
    transaction_digest: str,
) -> PurchaseReceipt:
    """Completes a POD purchase through the wallet-and-chain adapter seam.

    Args:
        listing: Fixed-price POD listing to purchase.
        buyer_id: Buyer identifier for the purchased listing.
        environment: Wallet and chain assumptions for the purchase flow.
        transaction_digest: Recorded transaction or simulated transaction id.

    Returns:
        A purchase receipt that keeps environment assumptions explicit while
        returning the purchased listing state.
    """

    purchased_listing = purchase_pod_listing(listing, buyer_id=buyer_id)

    return PurchaseReceipt(
        environment=environment,
        transaction_digest=transaction_digest,
        purchased_listing=purchased_listing,
    )
