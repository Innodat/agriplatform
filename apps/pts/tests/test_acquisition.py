from apps.pts.backend.acquisition import acquisition_catalogue

def test_acquisition_priorities_are_separate_from_poem_rights_and_counts():
    sources=[{'id':'MAU-2023','rights_id':'UNCHANGED'}]
    result=acquisition_catalogue(sources)
    assert set(result['acquisition'])=={'MAU-2023'}
    assert len(result['acquisition_leads'])==12
    ids=[p['id'] for p in result['acquisition_leads']]
    assert len(ids)==len(set(ids))
    assert sources==[{'id':'MAU-2023','rights_id':'UNCHANGED'}]
    assert not any('text' in p or 'eligible_for_private_training' in p for p in result['acquisition_leads'])
    for p in result['acquisition_leads']:
        assert p['priority'] in ('high','promising')
        assert p['reason'] and p['next_step'] and p['rights_note']
        assert p['source_url'].startswith('https://')
        if p.get('contact'):
            assert p['contact']['url'].startswith('https://')
            assert p['contact']['verified_on']=='2026-10-12'
