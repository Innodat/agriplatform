"""Synthetic Access seam; real KDG FastAPI/Uvicorn. No shared service import or DB."""
import sys, socket, json
from pathlib import Path
from datetime import datetime, timezone
import httpx, uvicorn
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'api'))
from main import create_app
ACCOUNT='11111111-1111-4111-8111-111111111111'
ORG='33333333-3333-4333-8333-333333333333'
mode_path=Path(sys.argv[1])
def access(request):
    assert request.headers['x-service-key']=='SYNTHETIC-SERVER-ONLY'
    mode=mode_path.read_text().strip()
    if mode=='denied': return httpx.Response(403,json={'detail':{'code':'access_denied'}})
    if mode=='unavailable': raise httpx.ConnectError('PRIVATE',request=request)
    return httpx.Response(200,json={'account_id':ACCOUNT,'actor_id':'44444444-4444-4444-8444-444444444444','membership_id':'1','authorization_scope':{'kind':'organization','org_id':ORG},'resource_scope':{'kind':'own_account','account_id':ACCOUNT},'permission':'kdg_capture.capture.read.own','decision_id':'55555555-5555-4555-8555-555555555555','checked_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')})
app=create_app(org_id=ORG,access_url='https://access.synthetic.invalid',service_key='SYNTHETIC-SERVER-ONLY',transport=httpx.MockTransport(access))
sock=socket.socket();sock.bind(('127.0.0.1',0))
print(json.dumps({'port':sock.getsockname()[1]}),flush=True)
uvicorn.run(app,fd=sock.fileno(),access_log=False,log_level='critical',timeout_graceful_shutdown=2)
