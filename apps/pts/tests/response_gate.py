"""Fixture-only transparent control-response delay; never serves file bytes.

The real PtS/Identity/provider make every decision. This holds one already-issued
Set-Cookie response at the ingress boundary to exercise actual browser arrival.
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time
from fastapi import FastAPI,Request
from fastapi.responses import Response
import httpx

app=FastAPI(docs_url=None,openapi_url=None)

@app.get('/health')
def health():return {'status':'running'}

@app.api_route('/api/{path:path}',methods=['POST','OPTIONS'])
async def proxy(path:str,request:Request):
    control=Path(os.environ['PTS_FIXTURE_GATE_CONTROL'])
    upstream=os.environ['PTS_FIXTURE_GATE_UPSTREAM']
    if (control/'file-origin-unavailable').exists() or (path=='file-session/clear' and (control/'clear-unavailable').exists()):
        return Response('{"detail":{"code":"fixture_file_origin_unavailable"}}',status_code=503,
                        headers={'Content-Type':'application/json','Cache-Control':'private, no-store'})
    async with httpx.AsyncClient(trust_env=False,follow_redirects=False,timeout=30) as client:
        response=await client.request(request.method,upstream+request.url.path,params=request.query_params,content=await request.body(),headers={name:value for name,value in request.headers.items() if name.lower() in ('host','authorization','cookie','origin','content-type','sec-fetch-site')})
    assert len(response.content)<=65536,'fixture_control_response_too_large'
    held=False
    if path=='file-session' and request.method=='POST' and response.status_code==200:
        try:(control/'armed').unlink();held=True
        except FileNotFoundError:pass
    preparation=False;preparation_mode=None;pair_matches=None
    if path=='file-session/prepare' and request.method=='POST' and response.status_code==200:
        # One private-fault case needs every real response for this exact pair
        # held: the live SDK may issue another valid preparation while the first
        # is delayed. Keep the ordinary single-response modes unchanged.
        all_pair_arm=control/'prepare-all-pair-armed'
        if all_pair_arm.exists():
            expected_pair=json.loads(all_pair_arm.read_text());actual=response.json()
            pair_matches={'account_matches_expected':actual.get('account_id')==expected_pair['account_id'],
                          'session_matches_expected':actual.get('session_id')==expected_pair['session_id']}
            if all(pair_matches.values()):preparation=True;preparation_mode='verified-owner-pair-all'
        pair_arm=control/'prepare-pair-armed'
        if pair_arm.exists():
            expected_pair=json.loads(pair_arm.read_text());actual=response.json()
            pair_matches={'account_matches_expected':actual.get('account_id')==expected_pair['account_id'],
                          'session_matches_expected':actual.get('session_id')==expected_pair['session_id']}
            if all(pair_matches.values()):
                pair_arm.unlink();preparation=True;preparation_mode='verified-owner-pair'
        try:
            expected=(control/'prepare-armed').read_text()
            token_matches=hashlib.sha256(request.headers.get('authorization','').encode()).hexdigest()==expected
            if (control/'prepare-pair-observation').exists():
                pair=json.loads((control/'prepare-pair-observation').read_text());actual=response.json()
                with (control/'prepare-observations.jsonl').open('a') as observations:
                    observations.write(json.dumps({'actual_upstream_status':response.status_code,'token_matches_armed':token_matches,
                        'account_matches_expected':actual.get('account_id')==pair['account_id'],
                        'session_matches_expected':actual.get('session_id')==pair['session_id']})+'\n')
            if token_matches:
                (control/'prepare-armed').unlink();preparation=True;preparation_mode='exact-original-credential'
        except FileNotFoundError:pass
    clear_mode=False
    clear_arm=control/'clear-pair-armed'
    if path=='file-session/clear' and request.method=='POST' and response.status_code==200 and clear_arm.exists():
        expected_pair=json.loads(clear_arm.read_text());actual=response.json()
        matches={'account_matches_expected':actual.get('account_id')==expected_pair['account_id'],
                 'session_matches_expected':actual.get('session_id')==expected_pair['session_id']}
        if all(matches.values()):
            clear_arm.unlink();clear_mode=True
            (control/'clear-held').write_text(json.dumps({'actual_upstream_status':response.status_code,**matches}))
            deadline=time.monotonic()+30
            while not (control/'clear-release').exists():
                if time.monotonic()>deadline:raise RuntimeError('fixture_clear_gate_deadline')
                await asyncio.sleep(.05)
            (control/'clear-released').write_text('released')
    if preparation:
        (control/'prepare-held').write_text(json.dumps({'actual_upstream_status':200,'set_cookie_present':'set-cookie' in response.headers,'matched_by':preparation_mode,**(pair_matches or {})}))
        deadline=time.monotonic()+30
        while not (control/'prepare-release').exists():
            if time.monotonic()>deadline:raise RuntimeError('fixture_preparation_gate_deadline')
            await asyncio.sleep(.05)
        (control/'prepare-released').write_text('released')
    if held:
        (control/'held').write_text(json.dumps({'actual_upstream_status':200,'set_cookie_present':'set-cookie' in response.headers}))
        deadline=time.monotonic()+30
        while not (control/'release').exists():
            if time.monotonic()>deadline:raise RuntimeError('fixture_response_gate_deadline')
            await asyncio.sleep(.05)
        (control/'released').write_text('released')
    headers={name:value for name,value in response.headers.items() if name.lower() in ('set-cookie','content-type','cache-control','referrer-policy','x-content-type-options','access-control-allow-origin','access-control-allow-credentials','vary')}
    # Observation-only fixture metadata identifies exactly the held response;
    # the actual App neither reads it nor changes behavior because of it.
    if preparation_mode in ('verified-owner-pair','verified-owner-pair-all'):headers['X-Fixture-Held-Preparation']=preparation_mode
    if clear_mode:headers['X-Fixture-Held-Clear']='verified-owner-pair'
    return Response(response.content,status_code=response.status_code,headers=headers)
