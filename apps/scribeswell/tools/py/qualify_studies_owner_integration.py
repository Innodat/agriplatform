"""Explicit single-use real owner integration; credentials stay in private evidence."""
import sys
import signal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
from studies_owner_fixture import qualify
if __name__=='__main__':
    def interrupted(signum,frame):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,interrupted)
    try:qualify()
    except KeyboardInterrupt:raise SystemExit(130) from None
    except Exception as error:
        print('studies_owner_integration_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
