from pathlib import Path
from apps.pts.tools.generate_contracts import generate

def test_generated_reader_contracts_have_no_drift():
    assert (Path(__file__).parents[1]/'web/src/contracts.ts').read_text()==generate()
