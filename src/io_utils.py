"""Reading, validating and writing CNF instances stored as JSON."""

import json
import sys
from pathlib import Path
from typing import Optional

import jsonschema

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "cnf_schema.json"


def _load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as file:
        return json.load(file)


def validate_instance(data: dict) -> None:
    """Validate an instance against the JSON Schema and the variable range.

    Raises:
        ValueError: if the instance is not a well-formed CNF formula.
    """
    try:
        jsonschema.validate(instance=data, schema=_load_schema())
    except jsonschema.ValidationError as error:
        location = "/".join(str(part) for part in error.absolute_path) or "root"
        raise ValueError(f"invalid instance at '{location}': {error.message}") from error

    # The schema cannot express this cross-field rule, so it is checked here.
    num_vars = data["num_vars"]
    for index, clause in enumerate(data["clauses"]):
        for literal in clause:
            if abs(literal) > num_vars:
                raise ValueError(
                    f"clause {index} uses literal {literal}, "
                    f"but num_vars is {num_vars}"
                )


def load_instance(path: Path) -> dict:
    """Read a SAT instance from a JSON file and validate it.

    Raises:
        OSError: if the file cannot be read.
        ValueError: if the content is not valid JSON or not a valid instance.
    """
    with open(path, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(f"not valid JSON ({error})") from error

    validate_instance(data)
    return {"num_vars": data["num_vars"], "clauses": data["clauses"]}


def format_instance(instance: dict) -> str:
    """Serialize an instance as JSON with one clause per line."""
    clauses = instance["clauses"]
    if clauses:
        body = ",\n".join(f"    {json.dumps(clause)}" for clause in clauses)
        clauses_text = f"[\n{body}\n  ]"
    else:
        clauses_text = "[]"
    return f'{{\n  "num_vars": {instance["num_vars"]},\n  "clauses": {clauses_text}\n}}\n'


def save_instance(instance: dict, path: Optional[Path] = None) -> None:
    """Write an instance as JSON to `path`, or to standard output if `path` is None.

    Raises:
        OSError: if the file cannot be written.
    """
    text = format_instance(instance)
    if path is None:
        sys.stdout.write(text)
        return

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
