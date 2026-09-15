"""Render the local design study without publishing guide text or approving claims."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--packets',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
packets=[json.loads(p.read_text()) for p in sorted(args.packets.glob('psalms-*.json'))]
if len(packets)!=4:
    raise ValueError('The design study needs all four visually curated guide packets')
text=json.dumps(packets,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
args.output.mkdir(parents=True,exist_ok=False)
with (args.output/'index.html').open('x') as out:
    out.write((root/'docs/pts-studio-concept.template.html').read_text().replace('<!--DATA-->',text))
print(args.output/'index.html')
