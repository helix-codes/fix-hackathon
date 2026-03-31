"""Deterministic shortage projections for tracked operational constraints.

This module projects time-to-shortage for fuel and other tracked resources
using explicit stock and burn-rate inputs. It also identifies which constraint
is expected to fail first for an operation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionInput:
    """Defines the stock and burn assumptions for one tracked constraint.

    Attributes:
        name: Planner-facing name of the tracked constraint.
        current_units: Current available stock.
        burn_rate_per_hour: Expected hourly consumption.
    """

    name: str
    current_units: float
    burn_rate_per_hour: float


@dataclass(frozen=True)
class ProjectionEntry:
    """Represents one projected shortage outcome.

    Attributes:
        name: Planner-facing name of the tracked constraint.
        hours_until_shortage: Projected time until the stock reaches zero.
    """

    name: str
    hours_until_shortage: float


@dataclass(frozen=True)
class ShortageProjection:
    """Represents the projected shortage order for an operation.

    Attributes:
        entries: Projection entries sorted by earliest shortage first.
        first_bottleneck_name: Name of the first projected bottleneck.
        first_bottleneck_hours: Hours until the first projected bottleneck.
    """

    entries: list[ProjectionEntry]
    first_bottleneck_name: str
    first_bottleneck_hours: float


def project_shortages(inputs: list[ProjectionInput]) -> ShortageProjection:
    """Projects time-to-shortage for tracked operational constraints.

    Args:
        inputs: Explicit stock and burn assumptions for each tracked
            constraint.

    Returns:
        A projection sorted by earliest shortage, including the first expected
        bottleneck.

    Raises:
        ValueError: A burn rate is not positive or no inputs are provided.
    """

    if not inputs:
        raise ValueError("At least one projection input is required.")

    if any(item.burn_rate_per_hour <= 0 for item in inputs):
        raise ValueError("Burn rate must be positive for all projection inputs.")

    entries = [
        ProjectionEntry(
            name=item.name,
            hours_until_shortage=item.current_units / item.burn_rate_per_hour,
        )
        for item in inputs
    ]

    entries = sorted(entries, key=lambda entry: entry.hours_until_shortage)
    first_entry = entries[0]

    return ShortageProjection(
        entries=entries,
        first_bottleneck_name=first_entry.name,
        first_bottleneck_hours=first_entry.hours_until_shortage,
    )
