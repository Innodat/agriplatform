"""Fixture ingress stays loopback-only and avoids an occupied adjacent port."""
import json
import socket
from types import SimpleNamespace
from apps.pts.tests.tls_acceptance import ROOT,http_listener_port,launch_gateway


def test_HTTP_port_does_not_use_an_occupied_TLS_adjacent_port():
    with socket.socket() as occupied:
        occupied.bind(('127.0.0.1',0));occupied.listen()
        occupied_port=occupied.getsockname()[1];tls_port=occupied_port-1
        selected=http_listener_port(tls_port)
        assert selected not in (tls_port,occupied_port)
        with socket.socket() as available:available.bind(('127.0.0.1',selected))


def test_fixture_gateway_declares_only_loopback_HTTP_and_TLS(monkeypatch,tmp_path):
    monkeypatch.syspath_prepend(str(ROOT/'platform/deployment'))
    monkeypatch.setattr('apps.pts.tests.tls_acceptance.http_listener_port',lambda port:45679)
    calls=[]
    def docker(*argv):calls.append(argv);return 'synthetic-container-id'
    fixture=SimpleNamespace(out=tmp_path,nonce='abc123',containers=[],docker=docker)
    launch_gateway(fixture,tmp_path,{'routes':[]},45677)
    settings=json.loads((tmp_path/'config.yaml').read_text())['apisix']
    assert settings['node_listen']==[{'ip':'127.0.0.1','port':45679}]
    assert settings['ssl']['listen']==[{'ip':'127.0.0.1','port':45677}]
    assert settings['enable_ipv6'] is False
    assert settings['enable_admin'] is settings['enable_control'] is False
    custody=json.loads((tmp_path/'gateway-container-custody.json').read_text())
    assert custody['listeners']=={'http':{'ip':'127.0.0.1','port':45679},'https':{'ip':'127.0.0.1','port':45677}}
    assert [argv[0] for argv in calls]==['create','start']
