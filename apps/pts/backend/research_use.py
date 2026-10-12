"""Read-only interpretation of recorded terms for one bounded private purpose.

This projection is not worldwide clearance and never edits source rights or approves
public release. Unknown/container-only rights stay visible as needing review.
"""
import re

SCOPE = 'private_noncommercial_psalm_ai_training'
PURPOSE = 'Private team research to train AI to generate Psalms.'
FUTURE_USE = 'A different purpose, public sharing or release needs a new rights assessment.'

def assessment(source, rights, poem=None):
    rights = rights or {}
    ai = rights.get('ai_use') if isinstance(rights.get('ai_use'), dict) else {}
    result = dict(scope=SCOPE, status='review', label='Rights need review',
                  summary='Permission for this private training purpose is not established in the recorded source terms.',
                  conditions=[FUTURE_USE], eligible_for_private_training=False,
                  public_release_assessed=False, source_id=source.get('id', ''), rights_id=source.get('rights_id', ''))
    if ai.get('private_model_training') is False:
        result['summary'] = 'The source record explicitly withholds model-training permission.'
        return result
    decision = ai.get('private_model_training')
    if isinstance(decision, dict) and decision.get('scope') == SCOPE:
        if decision.get('status') not in ['allowed', 'conditional']:return result
        result.update(status=decision['status'], label='Private training allowed' if decision['status']=='allowed' else 'Private training: conditions apply',
                      summary=decision.get('summary') or PURPOSE, conditions=list(decision.get('conditions') or [])+[FUTURE_USE], eligible_for_private_training=True)
        return result
    licence = str(rights.get('licence') or '')
    evidence = ' '.join(str(rights.get(k) or '') for k in ['assessment','scope','review_status']).lower()
    # A CC licence on a paper is not a grant for independently quoted poems.
    if any(s in evidence for s in ['conservative rights hold','independent full-text corpus reuse permission not established','independent poem rights unresolved','independent lyric rights unresolved','quoted_work_scope_review']) or ai.get('rights_tier') in ['quoted_work_scope_review','permission_needed_for_independent_poem_ai_use']:
        return result
    if re.search(r'article.level|third.party poem|quoted modern',licence+' '+evidence,re.I):return result
    working_pdf = bool(re.search(r'CC BY-NC-SA 4\.0 PDF',licence,re.I))
    if 'conflict' in (licence+' '+evidence).lower() and not working_pdf:return result
    if re.search(r'\bcc0\b|creativecommons\.org/publicdomain/zero/',licence,re.I):
        result.update(status='allowed',label='Private training allowed',summary='The recorded CC0 dedication supports reuse for this private project.',conditions=['Preserve source provenance for research reproducibility.',FUTURE_USE],eligible_for_private_training=True)
        return result
    match = re.search(r'\bcc\s+(by(?:-(?:nc|sa|nd)){0,2})\s+([234]\.\d)\b',licence,re.I)
    url = re.search(r'creativecommons\.org/licenses/(by(?:-(?:nc|sa|nd)){0,2})/([234]\.\d)',licence,re.I)
    code = 'BY-NC-SA' if working_pdf else match.group(1).upper() if match else url.group(1).upper() if url else None
    version='4.0' if working_pdf else match.group(2) if match else url.group(2) if url else None
    if code and 'ND' in code and version!='4.0':return result
    if code:
        restricted = code != 'BY' or working_pdf
        conditions = ['Keep author, source and licence information with the research material.', 'Use only within this private, noncommercial team project.', 'Hosted processing must remain for this project; do not authorise general provider model training.']
        if 'ND' in code:conditions.append('Do not share adaptations of the reference poems; public output/model reuse is not assessed here.')
        if 'SA' in code:conditions.append('Review ShareAlike obligations before sharing adapted material or a model.')
        if working_pdf:conditions.append('The broader CC BY catalogue notice remains unconfirmed; retain the PDF notice.')
        result.update(status='conditional' if restricted else 'allowed', label='Private training: conditions apply' if restricted else 'Private training allowed',
                      summary='Working terms: the PDF states CC BY-NC-SA 4.0. This private noncommercial purpose can use those terms.' if working_pdf else f'CC {code} {version} supports private use for this project when its conditions are met.',
                      conditions=conditions+[FUTURE_USE], eligible_for_private_training=True)
        return result
    # Do not treat older ND licences as having the 4.0 private-adaptation grant.
    if re.search(r'\bND\b|by-(?:nc-)?nd/',licence,re.I):return result
    historical = any(s in (licence+' '+evidence).lower() for s in ['public domain','public-domain','publicdomain/mark','no copyright','noc-nc'])
    mixed = 'mixed-source' in evidence or 'historical verses attributed' in evidence
    if mixed:
        creator=str((poem or {}).get('creator',{}).get('name') or '').lower()
        if not any(name in creator for name in ['muyaka','mwana kupona','mwanakupona','sayyid abdall']):return result
    if historical:
        result.update(status='conditional',label='Private training: conditions apply',
                      summary='The recorded assessment supports reuse of the original historical verse; this is not a licence for modern translations or commentary.',
                      conditions=['Use the original Swahili verse only; preserve source attribution.', 'The historical public-domain assessment applies where supported by the relevant law; repository copy terms remain applicable.']+[FUTURE_USE],
                      eligible_for_private_training=True)
        if 'noc-nc' in (licence+' '+evidence).lower() or 'non-commercial use only' in licence.lower():result['conditions'].insert(1,'Keep this acquired copy within noncommercial research use.')
    return result

def poem_usage(poem, library):
    source=next((s for s in library['sources'] if s['id']==poem['source_id']),{})
    rights=next((r for r in library['rights'] if r['id']==source.get('rights_id')),None)
    return assessment(source,rights,poem)

def source_usage(library):
    return {s['id']:assessment(s,next((r for r in library['rights'] if r['id']==s.get('rights_id')),None)) for s in library['sources']}
