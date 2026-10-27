"""Run one explicit frozen Access real-owner consumer qualification."""
import signal
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
from studies_frozen_runtime_fixture import qualify

if __name__=='__main__':
    def interrupted(signum,frame):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,interrupted)
    try:qualify()
    except KeyboardInterrupt:raise SystemExit(130) from None
    except Exception as error:
        print('studies_frozen_runtime_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
