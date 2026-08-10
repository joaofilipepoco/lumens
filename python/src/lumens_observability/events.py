"""Validated, trace-correlated business events with non-failing structured logging delivery."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from opentelemetry import trace

from lumens_observability.core import AttributePolicy


@dataclass(frozen=True)
class BusinessEvent:
    name: str
    attributes: Mapping[str, str]


BusinessEventSink = Callable[[BusinessEvent], None]


class BusinessEvents:
    def __init__(
        self,
        contract_version: str,
        required_attributes: Mapping[str, set[str]],
        attribute_policy: AttributePolicy,
        sink: BusinessEventSink,
    ) -> None:
        self._contract_version = contract_version
        self._required_attributes = {name: frozenset(attributes) for name, attributes in required_attributes.items()}
        self._policy = attribute_policy
        self._sink = sink

    def emit(self, name: str, attributes: Mapping[str, str]) -> bool:
        required = self._required_attributes.get(name)
        if required is None:
            return False
        accepted = dict(self._policy(attributes))
        if not required <= accepted.keys():
            return False
        envelope = {
            "event.name": name,
            "event.schema.version": self._contract_version,
            "lumens.contract.version": self._contract_version,
        }
        context = trace.get_current_span().get_span_context()
        if context.is_valid:
            envelope["trace_id"] = format(context.trace_id, "032x")
            envelope["span_id"] = format(context.span_id, "016x")
        envelope.update(accepted)
        try:
            self._sink(BusinessEvent(name, envelope))
        except Exception:
            return False
        return True


def structured_logging_sink(logger: logging.Logger) -> BusinessEventSink:
    """Return the default non-audit-grade structured logging event sink."""

    def emit(event: BusinessEvent) -> None:
        logger.info("lumens_business_event=%s", dict(event.attributes))

    return emit
