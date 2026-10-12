"""Public bibliographic acquisition research; never a poem rights decision."""
import json
from pathlib import Path

def acquisition_catalogue(sources):
    plans=json.loads(Path(__file__).with_name('acquisition_catalogue.json').read_text(encoding='utf-8'))
    ids={s['id'] for s in sources}
    return {'acquisition':{p['source_id']:p for p in plans if p.get('source_id') in ids},
            'acquisition_leads':[p for p in plans if not p.get('source_id')]}
