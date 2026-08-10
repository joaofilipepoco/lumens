from __future__ import annotations

import copy
from pathlib import Path

import pytest

from lumens_contract.cli import main
from lumens_contract.contract import ContractError, load_schema, load_yaml, merge_overlay, validate_contract


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "contract" / "lumens-contract.schema.json"
BASE = ROOT / "contract" / "lumens-contract.yaml"
OVERLAY = ROOT / "contract" / "examples" / "client-overlay.yaml"


def base_contract() -> dict:
    return load_yaml(BASE)


def test_base_contract_validates() -> None:
    validate_contract(base_contract(), load_schema(SCHEMA))


def test_overlay_merges_new_definitions() -> None:
    merged = merge_overlay(base_contract(), load_yaml(OVERLAY), load_schema(SCHEMA))
    assert "payment.authorize" in merged["operations"]
    assert "payment.provider" in merged["attributes"]


def test_overlay_cannot_redefine_base_definition() -> None:
    overlay = {"overlay": {"extends": "lumens", "version": "1.0.0"}, "attributes": {"integration.provider": base_contract()["attributes"]["integration.provider"]}}
    with pytest.raises(ContractError, match="redefines attributes"):
        merge_overlay(base_contract(), overlay, load_schema(SCHEMA))


def test_overlay_requires_matching_contract_version() -> None:
    overlay = {"overlay": {"extends": "lumens", "version": "2.0.0"}}
    with pytest.raises(ContractError, match="incompatible"):
        merge_overlay(base_contract(), overlay, load_schema(SCHEMA))


def test_high_cardinality_attribute_cannot_be_metric_dimension() -> None:
    contract = copy.deepcopy(base_contract())
    contract["attributes"]["integration.provider"]["cardinality"] = "high"
    with pytest.raises(ContractError, match="high cardinality"):
        validate_contract(contract, load_schema(SCHEMA))


def test_invalid_attribute_type_fails_schema_validation() -> None:
    contract = copy.deepcopy(base_contract())
    contract["attributes"]["integration.provider"]["type"] = "object"
    with pytest.raises(ContractError, match="Schema validation failed"):
        validate_contract(contract, load_schema(SCHEMA))


def test_invalid_namespace_is_rejected() -> None:
    contract = copy.deepcopy(base_contract())
    contract["contract"]["namespace"] = "Lumens Namespace"
    with pytest.raises(ContractError, match="Invalid namespace"):
        validate_contract(contract, load_schema(SCHEMA))


def test_duplicate_operation_outcome_is_rejected() -> None:
    contract = copy.deepcopy(base_contract())
    contract["operations"]["integration.enrich"]["outcomes"].append("success")
    with pytest.raises(ContractError, match="duplicate outcomes"):
        validate_contract(contract, load_schema(SCHEMA))


def test_duplicate_yaml_key_is_rejected(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text("contract: {}\ncontract: {}\n", encoding="utf-8")
    with pytest.raises(ContractError, match="Duplicate YAML key 'contract'"):
        load_yaml(duplicate)


def test_personal_attribute_cannot_be_metric_dimension() -> None:
    contract = copy.deepcopy(base_contract())
    contract["attributes"]["integration.provider"]["privacy"] = "personal"
    with pytest.raises(ContractError, match="personal"):
        validate_contract(contract, load_schema(SCHEMA))


def test_event_cannot_reference_unknown_attribute() -> None:
    contract = copy.deepcopy(base_contract())
    contract["events"]["integration.enrichment.completed"]["required_attributes"].append("unknown.attribute")
    with pytest.raises(ContractError, match="undefined attributes"):
        validate_contract(contract, load_schema(SCHEMA))


def test_generator_is_deterministic_and_check_detects_stale_files(tmp_path: Path) -> None:
    java = tmp_path / "LumensContract.java"
    python = tmp_path / "lumens_contract.py"
    command = [
        "generate",
        "--contract",
        str(BASE),
        "--schema",
        str(SCHEMA),
        "--overlay",
        str(OVERLAY),
        "--java-package",
        "com.example.contract",
        "--python-module",
        "example_contract",
        "--java-output",
        str(java),
        "--python-output",
        str(python),
    ]
    assert main(command) == 0
    first_java = java.read_text(encoding="utf-8")
    first_python = python.read_text(encoding="utf-8")
    assert 'OPERATION_PAYMENT_AUTHORIZE = "payment.authorize"' in first_java
    assert 'OPERATION_PAYMENT_AUTHORIZE = "payment.authorize"' in first_python
    assert 'ATTRIBUTE_PAYMENT_PROVIDER = "payment.provider"' in first_java
    assert 'ATTRIBUTE_PAYMENT_PROVIDER = "payment.provider"' in first_python
    assert main(command) == 0
    assert java.read_text(encoding="utf-8") == first_java
    assert python.read_text(encoding="utf-8") == first_python
    assert main([*command, "--check"]) == 0
    java.write_text("stale\n", encoding="utf-8")
    assert main([*command, "--check"]) == 1
