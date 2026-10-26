"""KDG-only strict metadata shared by closed own-read/edit observation owners."""
from copy import deepcopy
from context import positive_bigint_pattern

UTC_Z_PATTERN=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z(?![\s\S])'

def apply_observation_metadata(models):
    # Reuse identifier validation, preserving the receiving property's own title.
    identifier={key:deepcopy(value) for key,value in models['CaptureDetail']['properties']['org_id'].items() if key!='title'}
    for name in ('OwnReadObservation','OwnEditObservation','OrganizationScope','OwnAccountScope'):
        if name not in models:continue
        for field,prop in models[name]['properties'].items():
            if field.endswith('_id') and field!='membership_id':prop.update(deepcopy(identifier))
            if field=='membership_id':prop['pattern']=positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'
            if field in ('checked_at','expires_at'):prop.update(format='date-time',pattern=UTC_Z_PATTERN)
    return identifier
