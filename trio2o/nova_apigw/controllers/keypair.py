 # Copyright (c) 2017 VCCloud

import pecan
from pecan import expose, rest
import base64
import hashlib

import oslo_db.exception as db_exc

import trio2o.common.context as t_context
from trio2o.common.i18n import _
from trio2o.common import utils
from trio2o.db import core
from trio2o.db import models

def get_fingerprint(public_key):
    # Sa Pham. get finger print from public key
    key = base64.b64decode(public_key.strip().split()[1].encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))

class KeypairController(rest.RestController):
    def __init__(self, project_id):
        self.project_id = project_id

    @expose(generic=True, template='json')
    def post(self, **kw):

        context = t_context.extract_context_from_environ()

        if 'keypair' not in kw:
            utils.format_nova_error(400, _('keypair is not set'))
        required_fields = ['public_key', 'name']
        if not utils.validate_required_fields_set(kw['keypair'],
                                                  required_fields):
            utils.format_nova_error(
                400, _('Invalid input for field/attribute keypair.'))
        fingerprint = get_fingerprint(kw['keypair']['public_key'])

        keypair_dict = {
            'name': kw['keypair']['name'],
            'public_key': kw['keypair']['public_key'],
            'user_id': context.user_id,
            'fingerprint': fingerprint
        }
        try:
            with context.session.begin():
                keypair = core.create_resource(
                    context, models.KeyPair, keypair_dict)
        except Exception:
            return utils.format_nova_error(500, _('Failed to create keypair'))

        return {'keypair': keypair}

        @expose(generic=True, template='json')
        def get_all(self):
            context = t_context.extract_context_from_environ()
            with context.session.begin():
                keypairs = core.query_resource(context, models.KeyPair,
                                            [], [])
                return {'keypair': [dict(
                    [('name', keypair['name']),
                    ('fingerprint', keypair['fingerprint'])]) for keypair in keypairs]}
