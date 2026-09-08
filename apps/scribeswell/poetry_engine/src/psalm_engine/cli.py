"""Local research CLI; failures exit nonzero with their original exception."""

import argparse
import csv
import json
import logging
import shlex
from pathlib import Path

from .alignment import align_tokens
from .experiment import prepare_experiment, run_experiment, save_evaluations
from .fetch import fetch_bhsa
from .generation import CommandGenerator
from .models import CanonicalPsalmRepresentation, Claim, Source, Token
from .sources import ingest_pdf, load_bhsa, load_morphhb
from .storage import write_json


def build(args) -> None:
    source, left, units = load_morphhb(args.morphhb, args.psalm, args.morphhb_revision)
    sources, tokens = [source], list(left)
    right: list[Token] = []
    if args.bhsa:
        source, right, extra_units = load_bhsa(args.bhsa, args.psalm)
        sources.append(source)
        tokens.extend(right)
        units.extend(extra_units)
    claims, principles = [], []
    if args.annotations:
        claims = [
            Claim.model_validate_json(line)
            for line in args.annotations.read_text().splitlines()
            if line.strip()
        ]
    if args.principles:
        principles = [
            Claim.model_validate_json(line)
            for line in args.principles.read_text().splitlines()
            if line.strip()
        ]
    for pdf in args.pdf_evidence or []:
        sources.append(Source.model_validate(json.loads(pdf.read_text())["source"]))
    rep = CanonicalPsalmRepresentation(
        psalm=args.psalm,
        sources=sources,
        tokens=tokens,
        units=units,
        alignments=align_tokens(left, right),
        claims=claims,
        principles=principles,
        limitations=[
            "Consonantal alignment is heuristic and awaits human review.",
            "No melody supplied; no claim of full singability.",
            "No automatically inferred poetic or theological interpretation is treated as fact.",
        ],
    )
    write_json(args.output, rep)
    write_json(
        args.output.with_suffix(".alignment.json"),
        {
            "representation_id": rep.representation_id,
            "morphhb_tokens": len(left),
            "bhsa_tokens": len(right),
            "unmatched_groups": sum(a.status == "unmatched" for a in rep.alignments),
            "groups": [a.model_dump() for a in rep.alignments],
        },
    )
    print(args.output)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Psalm translation research; generated outputs are drafts"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    schema = commands.add_parser(
        "schema", help="Write the versioned canonical representation JSON schema"
    )
    schema.add_argument("--output", type=Path, required=True)
    fetch = commands.add_parser(
        "fetch-bhsa", help="Download pinned CC-BY-NC-4.0 source features for noncommercial research"
    )
    fetch.add_argument("--revision", required=True)
    fetch.add_argument("--output", type=Path, required=True)
    fetch.add_argument("--version", default="2021")
    builder = commands.add_parser(
        "build-representation", help="Load sources, align all tokens, validate and save JSON"
    )
    builder.add_argument("--psalm", type=int, default=23)
    builder.add_argument("--morphhb", type=Path, required=True)
    builder.add_argument("--morphhb-revision", required=True)
    builder.add_argument("--bhsa", type=Path)
    builder.add_argument("--annotations", type=Path)
    builder.add_argument("--principles", type=Path)
    builder.add_argument("--pdf-evidence", type=Path, action="append")
    builder.add_argument("--output", type=Path, required=True)
    validator = commands.add_parser("validate-representation")
    validator.add_argument("path", type=Path)
    pdf = commands.add_parser("ingest-pdf")
    pdf.add_argument("path", type=Path)
    pdf.add_argument("--output", type=Path, required=True)
    experiment = commands.add_parser(
        "experiment", help="Prepare exact requests; optionally generate through a provider runner"
    )
    experiment.add_argument("--representation", type=Path, required=True)
    experiment.add_argument("--output", type=Path, default=Path("runs"))
    experiment.add_argument(
        "--conditions", nargs="+", choices=list("ABCD"), default=["A", "B", "C"]
    )
    experiment.add_argument("--provider", required=True)
    experiment.add_argument("--model", required=True)
    experiment.add_argument(
        "--mode", choices=["literal", "poetic", "song-oriented-without-melody"], default="poetic"
    )
    experiment.add_argument(
        "--settings", default="{}", help="JSON model settings; never include credentials"
    )
    experiment.add_argument("--runner", help="Executable and arguments; parsed without a shell")
    execute = commands.add_parser("run", help="Execute an already prepared run once")
    execute.add_argument("path", type=Path)
    execute.add_argument("--runner", required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("path", type=Path, help="Experiment directory")
    evaluate.add_argument("--evaluations", type=Path, required=True)
    annotations = commands.add_parser("validate-annotations")
    annotations.add_argument("path", type=Path)
    annotations.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if args.command == "schema":
        write_json(args.output, CanonicalPsalmRepresentation.model_json_schema())
    elif args.command == "fetch-bhsa":
        fetch_bhsa(args.output, args.revision, args.version)
    elif args.command == "build-representation":
        build(args)
    elif args.command == "validate-representation":
        rep = CanonicalPsalmRepresentation.model_validate_json(args.path.read_text())
        print(f"Validated Psalm {rep.psalm}, {len(rep.tokens)} source tokens")
    elif args.command == "ingest-pdf":
        ingest_pdf(args.path, args.output)
    elif args.command == "experiment":
        rep = CanonicalPsalmRepresentation.model_validate_json(args.representation.read_text())
        run = prepare_experiment(
            rep,
            args.output,
            args.conditions,
            args.provider,
            args.model,
            args.mode,
            json.loads(args.settings),
        )
        print(run, flush=True)
        if args.runner:
            run_experiment(run, CommandGenerator(shlex.split(args.runner)))
    elif args.command == "run":
        run_experiment(args.path, CommandGenerator(shlex.split(args.runner)))
    elif args.command == "evaluate":
        print(save_evaluations(args.path, args.evaluations))
    elif args.command == "validate-annotations":
        claims = [
            Claim.model_validate_json(line)
            for line in args.path.read_text().splitlines()
            if line.strip()
        ]
        if not claims:
            raise ValueError("Annotation file is empty")
        if args.csv:
            with args.csv.open("x", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "id",
                        "category",
                        "value",
                        "reviewer_status",
                        "reviewer",
                        "revision",
                    ],
                )
                writer.writeheader()
                writer.writerows({k: c.model_dump()[k] for k in writer.fieldnames} for c in claims)
        print(f"Validated {len(claims)} annotations")


if __name__ == "__main__":
    main()
