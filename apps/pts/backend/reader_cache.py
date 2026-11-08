"""Validators for authorized corpus JSON only, never files or exported artifacts."""
import hashlib
import json
from fastapi import Response

# Bump when a projection's meaning changes without changing its serialized data.
REPRESENTATION_VERSION = 'pts-reader-1'


def conditional_json(request, response, model, result, account, representation):
    # Validate/default the same representation FastAPI sends before hashing it.
    body = model.model_validate(result).model_dump(mode='json')
    stable = dict(body)
    stable.pop('exported_at', None)
    if 'evidence' in stable:
        stable['evidence'] = {k:v for k,v in stable['evidence'].items() if k!='exported_at'}
    content = json.dumps([REPRESENTATION_VERSION, account, representation, stable],
                         ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    etag = 'W/"' + hashlib.sha256(content).hexdigest() + '"'
    # RFC weak comparison for GET: accept strong equivalents and validator lists.
    validators = request.headers.get('if-none-match', '')
    tags = [tag.strip().removeprefix('W/') for tag in validators.split(',')]
    if '*' in tags or etag[2:] in tags:
        return Response(status_code=304, headers={'ETag':etag})
    response.headers['ETag'] = etag
    return body
