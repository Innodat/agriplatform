"""Pure private migration release evidence; no runtime or environment selection."""
OWNER = 'scribeswell_studies'
TARGET = 'scribeswell_studies_0009'
REVISIONS = tuple(f'scribeswell_studies_{number:04d}' for number in range(1, 10))
FIELDS = {'complete', 'owner', 'before', 'after', 'recovery'}


def valid_result(value):
    """Accept only the intended release and a declared observed starting revision."""
    return (type(value) is dict and set(value) == FIELDS
            and value['complete'] is True and value['owner'] == OWNER
            and (value['before'] is None or
                 (type(value['before']) is str and value['before'] in REVISIONS))
            and value['after'] == TARGET and value['recovery'] == 'forward-only')
