"""Validation, overlay merging, and deterministic source generation."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


class ContractError(ValueError):
    """A contract or overlay violates Lumens semantic rules."""


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ContractError(f"Duplicate YAML key '{key}' at line {key_node.start_mark.line + 1}.")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
JAVA_IDENTIFIER_PATTERN = re.compile(r"[^A-Z0-9]+")
PYTHON_IDENTIFIER_PATTERN = re.compile(r"[^a-z0-9]+")
EXTENDABLE_SECTIONS = ("operations", "attributes", "events", "metric_dimensions", "baggage")


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML mapping and convert parser errors to contract errors."""
    try:
        content = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except OSError as error:
        raise ContractError(f"Cannot read '{path}': {error}") from error
    except yaml.YAMLError as error:
        raise ContractError(f"Invalid YAML in '{path}': {error}") from error
    if not isinstance(content, dict):
        raise ContractError(f"'{path}' must contain a YAML mapping.")
    return content


def load_schema(path: Path) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ContractError(f"Cannot read schema '{path}': {error}") from error
    except json.JSONDecodeError as error:
        raise ContractError(f"Invalid JSON Schema in '{path}': {error}") from error
    if not isinstance(schema, dict):
        raise ContractError(f"Schema '{path}' must contain an object.")
    return schema


def validate_schema(contract: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate structure and surface the first deterministic schema error."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(contract), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "contract"
        raise ContractError(f"Schema validation failed at '{location}': {error.message}")


def validate_contract(contract: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Validate schema and Lumens rules that need cross-reference checks."""
    validate_schema(contract, schema)
    namespace = contract["contract"]["namespace"]
    if not NAME_PATTERN.fullmatch(namespace):
        raise ContractError(f"Invalid namespace '{namespace}'. Use lowercase dot, dash, or underscore separated names.")

    attributes = contract.get("attributes", {})
    _validate_names("attribute", attributes)
    _validate_names("operation", contract.get("operations", {}))
    _validate_names("event", contract.get("events", {}))
    _validate_names("metric dimension", contract.get("metric_dimensions", {}))
    _validate_names("baggage key", contract.get("baggage", {}))
    _validate_constant_collisions("attribute", attributes, _java_identifier)
    _validate_constant_collisions("attribute", attributes, _python_identifier)

    for name, attribute in attributes.items():
        if attribute["privacy"] in {"personal", "secret"} and attribute.get("metric_dimension"):
            raise ContractError(f"Attribute '{name}' is {attribute['privacy']} and cannot be a metric dimension.")
        if attribute["cardinality"] == "high" and attribute.get("metric_dimension"):
            raise ContractError(f"Attribute '{name}' has high cardinality and cannot be a metric dimension.")

    for name, operation in contract.get("operations", {}).items():
        outcomes = operation.get("outcomes", [])
        if len(set(outcomes)) != len(outcomes):
            raise ContractError(f"Operation '{name}' contains duplicate outcomes.")

    for name, event in contract.get("events", {}).items():
        required = set(event.get("required_attributes", []))
        optional = set(event.get("optional_attributes", []))
        overlap = required & optional
        if overlap:
            raise ContractError(f"Event '{name}' has required and optional attributes in common: {', '.join(sorted(overlap))}.")
        unknown = (required | optional) - set(attributes)
        if unknown:
            raise ContractError(f"Event '{name}' references undefined attributes: {', '.join(sorted(unknown))}.")

    for name, dimension in contract.get("metric_dimensions", {}).items():
        source = dimension["attribute"]
        if source not in attributes:
            raise ContractError(f"Metric dimension '{name}' references undefined attribute '{source}'.")
        attribute = attributes[source]
        if attribute["cardinality"] != "bounded" or attribute["privacy"] in {"personal", "secret"}:
            raise ContractError(f"Metric dimension '{name}' must reference a public or internal bounded attribute.")


def merge_overlay(base: Mapping[str, Any], overlay: Mapping[str, Any], schema: Mapping[str, Any]) -> dict[str, Any]:
    """Add overlay definitions without allowing redefinition of base semantics."""
    if "overlay" not in overlay:
        raise ContractError("Overlay must declare an 'overlay' mapping.")
    overlay_info = overlay["overlay"]
    if not isinstance(overlay_info, Mapping):
        raise ContractError("Overlay field 'overlay' must be a mapping.")
    base_contract = base["contract"]
    target = overlay_info.get("extends")
    if target != base_contract["name"]:
        raise ContractError(f"Overlay extends '{target}', expected '{base_contract['name']}'.")
    version = overlay_info.get("version")
    if version != base_contract["version"]:
        raise ContractError(f"Overlay version '{version}' is incompatible with base version '{base_contract['version']}'.")

    merged = copy.deepcopy(dict(base))
    for key, value in overlay.items():
        if key == "overlay":
            continue
        if key not in EXTENDABLE_SECTIONS:
            raise ContractError(f"Overlay cannot define top-level field '{key}'.")
        if not isinstance(value, Mapping):
            raise ContractError(f"Overlay section '{key}' must be a mapping.")
        existing = merged.setdefault(key, {})
        duplicates = sorted(set(existing) & set(value))
        if duplicates:
            raise ContractError(f"Overlay redefines {key}: {', '.join(duplicates)}.")
        existing.update(copy.deepcopy(dict(value)))

    validate_contract(merged, schema)
    return merged


def _validate_names(kind: str, values: Mapping[str, Any]) -> None:
    for name in values:
        if not NAME_PATTERN.fullmatch(name):
            raise ContractError(f"Invalid {kind} name '{name}'.")


def _validate_constant_collisions(kind: str, values: Mapping[str, Any], normalizer: Any) -> None:
    seen: dict[str, str] = {}
    for name in values:
        constant = normalizer(name)
        if constant in seen:
            raise ContractError(f"{kind.capitalize()} names '{seen[constant]}' and '{name}' generate the same constant '{constant}'.")
        seen[constant] = name


def _java_identifier(value: str) -> str:
    return JAVA_IDENTIFIER_PATTERN.sub("_", value.upper()).strip("_")


def _python_identifier(value: str) -> str:
    return PYTHON_IDENTIFIER_PATTERN.sub("_", value.lower()).strip("_")


def generate_java(contract: Mapping[str, Any], package: str) -> str:
    """Generate deterministic Java constants for contract names."""
    package_name = package.strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", package_name):
        raise ContractError(f"Invalid Java package '{package}'.")
    lines = [
        "// Generated by lumens-contract. Do not edit.",
        f"package {package_name};",
        "",
        "public final class LumensContract {",
        "  private LumensContract() {}",
        "",
        f'  public static final String CONTRACT_NAME = "{contract["contract"]["name"]}";',
        f'  public static final String CONTRACT_VERSION = "{contract["contract"]["version"]}";',
        f'  public static final String NAMESPACE = "{contract["contract"]["namespace"]}";',
    ]
    _append_java_constants(lines, "ATTRIBUTE", contract.get("attributes", {}))
    _append_java_constants(lines, "OPERATION", contract.get("operations", {}))
    _append_java_constants(lines, "EVENT", contract.get("events", {}))
    _append_java_constants(lines, "METRIC_DIMENSION", contract.get("metric_dimensions", {}))
    _append_java_constants(lines, "BAGGAGE", contract.get("baggage", {}))
    lines.extend(["}", ""])
    return "\n".join(lines)


def _append_java_constants(lines: list[str], prefix: str, values: Mapping[str, Any]) -> None:
    for name in sorted(values):
        lines.append(f'  public static final String {prefix}_{_java_identifier(name)} = "{name}";')


def generate_python(contract: Mapping[str, Any], module: str) -> str:
    """Generate deterministic Python constants for contract names."""
    module_name = module.strip()
    if not re.fullmatch(r"[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*", module_name):
        raise ContractError(f"Invalid Python module '{module}'.")
    lines = [
        '"""Generated by lumens-contract. Do not edit."""',
        "",
        f'CONTRACT_NAME = "{contract["contract"]["name"]}"',
        f'CONTRACT_VERSION = "{contract["contract"]["version"]}"',
        f'NAMESPACE = "{contract["contract"]["namespace"]}"',
    ]
    _append_python_constants(lines, "ATTRIBUTE", contract.get("attributes", {}))
    _append_python_constants(lines, "OPERATION", contract.get("operations", {}))
    _append_python_constants(lines, "EVENT", contract.get("events", {}))
    _append_python_constants(lines, "METRIC_DIMENSION", contract.get("metric_dimensions", {}))
    _append_python_constants(lines, "BAGGAGE", contract.get("baggage", {}))
    lines.append("")
    return "\n".join(lines)


def _append_python_constants(lines: list[str], prefix: str, values: Mapping[str, Any]) -> None:
    for name in sorted(values):
        lines.append(f'{prefix}_{_python_identifier(name).upper()} = "{name}"')


def write_or_check(path: Path, content: str, check: bool) -> bool:
    """Write generated content, or report whether a checked file is current."""
    if check:
        return path.is_file() and path.read_text(encoding="utf-8") == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True
