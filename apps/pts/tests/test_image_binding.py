"""Image receipts may reference only owner or private adoption bundle custody."""
from pathlib import Path
import pytest
from apps.pts.tests import image_acceptance


def test_cleanup_image_reuse_is_explicit_and_other_phases_stay_bounded():
    assert image_acceptance.runtime_image_mode('cleanup',None) is None
    assert image_acceptance.runtime_image_mode('cleanup','private-binding')=='reuse'
    assert image_acceptance.runtime_image_mode('image-resources',None)=='prepare'
    for phase in ('owners','acceptance','browser','provider-storage'):
        with pytest.raises(ValueError,match='runtime_image_reuse_requires_qualified_phase'):
            image_acceptance.runtime_image_mode(phase,'private-binding')


def test_bundle_binding_preserves_legacy_default_and_accepts_private_clean_source(tmp_path,monkeypatch):
    monkeypatch.setattr(image_acceptance,'ROOT',tmp_path)
    default=tmp_path/'apps/pts/runtime-bundle';default.mkdir(parents=True)
    copied=tmp_path/'platform/deployment/.local/e1-pts-adoption/new/source/apps/pts/runtime-bundle';copied.mkdir(parents=True)
    assert image_acceptance.bundle_for_binding({})==default
    assert image_acceptance.bundle_for_binding({'bundle_path':str(copied.relative_to(tmp_path))})==copied


def test_bundle_binding_refuses_other_owner_absolute_traversal_and_symlink(tmp_path,monkeypatch):
    monkeypatch.setattr(image_acceptance,'ROOT',tmp_path)
    foreign=tmp_path/'services/access/runtime-bundle';foreign.mkdir(parents=True)
    link=tmp_path/'apps/pts/runtime-bundle';link.parent.mkdir(parents=True);link.symlink_to(foreign,target_is_directory=True)
    for value in (str(foreign),'../outside','services/access/runtime-bundle','apps/pts/runtime-bundle'):
        with pytest.raises(AssertionError,match='runtime_bundle_custody_invalid'):
            image_acceptance.bundle_for_binding({'bundle_path':value})
