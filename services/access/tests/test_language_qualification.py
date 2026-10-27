"""Qualification output custody fails before any network or business effect."""
import json
import os
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_language_preferences as qualifier

def test_existing_output_is_rejected_before_guard_or_auth(tmp_path,monkeypatch):
    output=tmp_path/'proof.json';output.write_text('retained evidence')
    monkeypatch.setattr(sys,'argv',['qualify','--fixture','unused','--output',str(output)])
    calls=[]
    monkeypatch.setattr(qualifier,'load',lambda _:calls.append('load'))
    monkeypatch.setattr(qualifier,'guard',lambda:calls.append('guard'))
    assert qualifier.main()==2
    assert calls==[] and output.read_text()=='retained evidence'
    assert not output.with_suffix('.json.attempts.jsonl').exists()

def test_durable_operation_journal_completes_short_writes(tmp_path,monkeypatch):
    proof=qualifier.Proof({},tmp_path/'new.json');actual=os.write;calls=[]
    def short(fd,data):
        calls.append(bytes(data));return actual(fd,data[:max(1,len(data)//2)])
    monkeypatch.setattr(os,'write',short)
    try:proof.record({'operation_id':'safe-operation','status':'attempting'})
    finally:os.close(proof.fd)
    rows=proof.output.with_suffix('.json.attempts.jsonl').read_text().splitlines()
    assert len(calls)>1 and [json.loads(row) for row in rows]==[{'operation_id':'safe-operation','status':'attempting'}]

def test_journal_zero_write_aborts_before_effect(tmp_path,monkeypatch):
    proof=qualifier.Proof({},tmp_path/'new.json')
    monkeypatch.setattr(os,'write',lambda *_:0)
    try:
        with pytest.raises(OSError):proof.record({'operation_id':'safe-operation','status':'attempting'})
    finally:os.close(proof.fd)
