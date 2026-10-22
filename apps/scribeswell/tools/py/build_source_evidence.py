"""Build a read-only source evidence candidate using only the standard library."""
import argparse
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from corpus_evidence import (EvidenceError, MAX_SOURCE_BYTES, build_source_candidate,
                             serialize_candidate)


def atomic_create(output, payload):
    """Publish one complete file without replacing an existing path, including symlinks."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix='.source-evidence-',
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)
    except FileExistsError:
        raise EvidenceError('output_exists') from None
    except OSError:
        raise EvidenceError('output_write_failed') from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                raise EvidenceError('output_cleanup_failed') from None


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'source_evidence.arguments_invalid\n')


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
        candidate = build_source_candidate(raw, **args)
        atomic_create(output, serialize_candidate(candidate))
    except EvidenceError as exc:
        print(exc.code, file=sys.stderr)
        return 1
    print('source_evidence.candidate_created')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
