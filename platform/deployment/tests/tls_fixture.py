"""Disposable CA and multi-PEM server lineage for TLS acceptance tests."""
import subprocess


def openssl(*args):
    return subprocess.check_output(['openssl', *map(str,args)], stderr=subprocess.DEVNULL)


def certificates(root, host='api.example.test'):
    ca=root/'ca.pem';cakey=root/'ca.key';key=root/'server.key';csr=root/'server.csr'
    openssl('req','-x509','-newkey','rsa:2048','-nodes','-days','5','-keyout',cakey,'-out',ca,'-subj','/CN=Disposable test CA')
    openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',key,'-out',csr,'-subj','/CN='+host)
    ext=root/'extensions';ext.write_text('subjectAltName=DNS:'+host+'\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n')
    leaf=root/'leaf.pem'
    # Exercise the previous parser's problematic no-padding case explicitly.
    for serial in (1,256,65536):
        openssl('x509','-req','-in',csr,'-CA',ca,'-CAkey',cakey,'-set_serial',serial,'-days','3','-extfile',ext,'-out',leaf)
        if len(openssl('x509','-in',leaf,'-outform','DER')) % 3 == 0: break
    else: raise AssertionError('could not construct unpadded leaf')
    chain=root/'fullchain.pem';chain.write_bytes(leaf.read_bytes()+ca.read_bytes())
    short=root/'short.pem'
    openssl('x509','-req','-in',csr,'-CA',ca,'-CAkey',cakey,'-set_serial','1000','-days','1','-extfile',ext,'-out',short)
    short.write_bytes(short.read_bytes()+ca.read_bytes())
    return ca,key,leaf,chain,short
