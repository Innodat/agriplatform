"""Focused parent proof using a fresh uniquely owned PG17 per selection."""
from pathlib import Path
import hashlib,json,os,secrets,signal,socket,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
PYTHON=str(ROOT/"apps/scribeswell/.local/owner-integration-20261027/python/bin/python")
def hashes():
 paths={}
 for base in [ROOT/"apps/scribeswell/backend",ROOT/"apps/scribeswell/tests",ROOT/"apps/scribeswell/studies-migrations",ROOT/"apps/scribeswell/studies-database-tools",ROOT/"apps/scribeswell/deployment"]:
  for p in base.rglob("*"):
   if p.is_file() and p.suffix in (".py",".json",".ini") and "__pycache__" not in p.parts:paths[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for n in ["platform/deployment/host-release.py","platform/deployment/registry.json","platform/deployment/tests/test_host.py"]:paths[n]=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
 return paths
def main():
 plan=json.loads((BASE/"native-plan.json").read_text());proof=BASE/plan["proof"];proof.mkdir(mode=0o700)
 before=hashes();(proof/"sources-before.json").write_text(json.dumps(before,indent=2)+"\n");results=[]
 for i,selection in enumerate(plan["selections"]):
  name="scribeswell-private-report-"+secrets.token_hex(10);ident=None;port=None;cleanup={};start=time.monotonic()
  try:
   ident=subprocess.check_output(["docker","run","-d","--name",name,"--label","scribeswell.fixture="+name,"-e","POSTGRES_PASSWORD=synthetic-only","-p","127.0.0.1::5432","postgres:17"],text=True).strip()
   data=json.loads(subprocess.check_output(["docker","inspect",ident]))[0];assert data["Config"]["Labels"]["scribeswell.fixture"]==name
   binding=data["NetworkSettings"]["Ports"]["5432/tcp"];assert len(binding)==1 and binding[0]["HostIp"]=="127.0.0.1";port=int(binding[0]["HostPort"]);assert port not in [55481,55482,55491,55492,55581,55582]
   until=time.monotonic()+45
   while subprocess.run(["docker","exec",ident,"pg_isready","-U","postgres"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
    if time.monotonic()>until:raise RuntimeError("owned_fixture_not_ready")
    time.sleep(.2)
   env={k:v for k,v in os.environ.items() if not(k.startswith("PG") or "NATIVE" in k or k.endswith("_DATABASE_URL") or k.endswith("_TEST_ADMIN_URL") or k in ["DATABASE_URL","PYTEST_ADDOPTS"])}
   env.update(PYTHONDONTWRITEBYTECODE="1",SCRIBESWELL_NOTES_TEST_ADMIN_URL="postgresql://postgres:synthetic-only@127.0.0.1:"+str(port)+"/postgres",SCRIBESWELL_TEST_PYTHON=PYTHON)
   argv=[PYTHON,"-m","pytest","-q",selection,"-rs","--tb=short"]
   with (proof/("native-"+str(i)+".log")).open("w") as out:
    os.chmod(out.name,0o600);r=subprocess.run(argv,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=600)
   results.append({"argv":argv,"exit_code":r.returncode,"elapsed_seconds":round(time.monotonic()-start,2),"container_id":ident,"port":port})
  finally:
   if ident:
    data=json.loads(subprocess.check_output(["docker","inspect",ident]))[0];assert data["Config"]["Labels"]["scribeswell.fixture"]==name
    subprocess.run(["docker","stop","--time","10",ident],check=True,stdout=subprocess.DEVNULL)
    data=json.loads(subprocess.check_output(["docker","inspect",ident]))[0];assert not data["State"]["Running"]
    cleanup={"stopped":True,"exit_code":data["State"]["ExitCode"],"forced":data["State"]["ExitCode"]==137};assert not cleanup["forced"]
    subprocess.run(["docker","rm","-v",ident],check=True,stdout=subprocess.DEVNULL);cleanup["removed"]=True
    with socket.socket() as s:s.bind(("127.0.0.1",port));cleanup["port_released"]=True
   if results:results[-1]["cleanup"]=cleanup
   after=hashes();record={"results":results,"sources_unchanged":before==after,"sources_after":after};(proof/"results.json").write_text(json.dumps(record,indent=2)+"\n")
  if results[-1]["exit_code"]:break
 print(json.dumps({"proof":str(proof),"results":results,"sources_unchanged":record["sources_unchanged"]}));return int(not record["sources_unchanged"] or any(x["exit_code"] for x in results))
if __name__=="__main__":
 def interrupted(*_):raise KeyboardInterrupt()
 signal.signal(signal.SIGTERM,interrupted)
 try:raise SystemExit(main())
 except KeyboardInterrupt:raise SystemExit(130) from None
 except Exception as error:
  print("private_report_native_failed:"+type(error).__name__);raise SystemExit(1) from None
