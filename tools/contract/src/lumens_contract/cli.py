"""Command-line interface for the Lumens semantic contract tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lumens_contract.contract import (
    ContractError,
    generate_java,
    generate_python,
    load_schema,
    load_yaml,
    merge_overlay,
    validate_contract,
    write_or_check,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lumens-contract")
    subcommands = parser.add_subparsers(dest="command", required=True)
    generate = subcommands.add_parser("generate", help="validate a contract and generate constants")
    generate.add_argument("--contract", type=Path, default=Path("contract/lumens-contract.yaml"))
    generate.add_argument("--schema", type=Path, default=Path("contract/lumens-contract.schema.json"))
    generate.add_argument("--overlay", type=Path)
    generate.add_argument("--java-package", default="com.deloitte.lumens.contract")
    generate.add_argument("--python-module", default="lumens_contract.generated")
    generate.add_argument("--java-output", type=Path, default=Path("contract/generated/LumensContract.java"))
    generate.add_argument("--python-output", type=Path, default=Path("contract/generated/lumens_contract.py"))
    generate.add_argument("--check", action="store_true", help="fail when generated files are stale")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        schema = load_schema(args.schema)
        contract = load_yaml(args.contract)
        validate_contract(contract, schema)
        if args.overlay:
            contract = merge_overlay(contract, load_yaml(args.overlay), schema)
        java = generate_java(contract, args.java_package)
        python = generate_python(contract, args.python_module)
        java_current = write_or_check(args.java_output, java, args.check)
        python_current = write_or_check(args.python_output, python, args.check)
        if args.check and not (java_current and python_current):
            stale = []
            if not java_current:
                stale.append(str(args.java_output))
            if not python_current:
                stale.append(str(args.python_output))
            raise ContractError(f"Generated files are stale or missing: {', '.join(stale)}.")
    except ContractError as error:
        print(f"lumens-contract: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
