"""Supervisor exit classification distinguishes graceful TERM from forced stops."""
import pytest
from apps.pts.tests.resource_acceptance import graceful_exit


@pytest.mark.parametrize('code,container,oom,accepted',[
    (0,False,False,True),(-15,False,False,True),(143,True,False,True),(0,True,False,True),
    (-9,False,False,False),(137,True,False,False),(0,True,True,False),
    (1,False,False,False),(70,True,False,False),(143,False,False,False),(-15,True,False,False)])
def test_only_zero_or_runtime_specific_unforced_TERM_is_accepted(code,container,oom,accepted):
    assert graceful_exit(code,container=container,oom=oom) is accepted
