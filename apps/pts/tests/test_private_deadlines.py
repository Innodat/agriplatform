"""The declared whole-response deadline covers preflight and active bytes."""
import asyncio
import pytest
import httpx
from fastapi import HTTPException
from starlette.requests import Request
from apps.pts.backend import private_stream as stream_module
from apps.pts.tests.test_private_stream import Client,ID,ACCOUNT,ACTOR,OPERATION,BUFFER


class Slow(httpx.AsyncByteStream):
    def __init__(self,preflight):self.preflight=preflight;self.closed=False
    async def __aiter__(self):
        if self.preflight:await asyncio.sleep(1)
        yield b'a'*BUFFER
        yield b'b'*BUFFER
        await asyncio.sleep(1)
        yield b'c'*BUFFER
    async def aclose(self):self.closed=True


@pytest.mark.parametrize('preflight',[True,False])
def test_total_deadline_bounds_preflight_and_active_stream_and_returns_capacity(monkeypatch,preflight):
    monkeypatch.setattr(stream_module,'TOTAL_SECONDS',.03)
    async def run():
        source=Slow(preflight);capacity=stream_module.Capacity()
        request=Request({'type':'http','method':'GET','headers':[]});messages=[]
        if preflight:
            with pytest.raises(HTTPException) as failed:
                await stream_module.prepare(Client(source),ID,{'account_id':ACCOUNT},ACTOR,OPERATION,request,'download','private.pdf',capacity)
            assert failed.value.status_code==503
        else:
            response=await stream_module.prepare(Client(source),ID,{'account_id':ACCOUNT},ACTOR,OPERATION,request,'download','private.pdf',capacity)
            async def send(message):messages.append(message)
            async def receive():await asyncio.sleep(2)
            with pytest.raises(TimeoutError):await response({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
            bodies=[value for value in messages if value['type']=='http.response.body']
            assert sum(len(value.get('body',b'')) for value in bodies)==BUFFER
            assert all(value.get('more_body') for value in bodies)
        assert source.closed and capacity.active==0 and capacity.accounts=={}
    asyncio.run(run())
