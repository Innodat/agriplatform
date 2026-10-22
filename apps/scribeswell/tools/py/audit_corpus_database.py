"""Compare a qualified source artifact with one read-only runtime database snapshot."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from corpus_evidence import EvidenceError, MAX_SOURCE_BYTES
from corpus_database_audit import audit_database, serialize_audit_candidate
from build_source_evidence import SafeParser, atomic_create


def main():
    parser = SafeParser(description=__doc__)
    for option in ('source', 'expected-source-sha256', 'source-id', 'catalogue-version',
                   'versification-id', 'tokenization-version', 'output'):
        parser.add_argument('--' + option, required=True)
    args = vars(parser.parse_args())
    try:
        source = Path(args.pop('source'))
        output = Path(args.pop('output'))
        try:
            with source.open('rb') as stream:
                raw = stream.read(MAX_SOURCE_BYTES + 1)
        except OSError:
            raise EvidenceError('source_read_failed') from None
        candidate = audit_database(raw, database_url=os.environ.get('SCRIBESWELL_AUDIT_DATABASE_URL'), **args)
        atomic_create(output, serialize_audit_candidate(candidate))
    except EvidenceError as exc:
        print(exc.code, file=sys.stderr)
        return 1
    print('database_audit.candidate_created')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
