 # Copyright (c) 2017 VCCloud

import pecan
from pecan import expose, rest
import base64
import hashlib

import oslo_db.exception as db_exc

import trio2o.common.context as t_context
import trio2o.common.client as t_client
from trio2o.common import constants

from trio2o.common.i18n import _
from trio2o.common import utils
import trio2o.db.api as db_api
from trio2o.db import core
from trio2o.db import models

class ExtensionController(rest.RestController):
    def __init__(self, project_id):
        self.project_id = project_id
        self.clients = {constants.TOP: t_client.Client()}

    def _get_client(self, pod_name=constants.TOP):
        if pod_name not in self.clients:
            self.clients[pod_name] = t_client.Client(pod_name)
        return self.clients[pod_name]

    @expose(generic=True, template='json')
    def get(self):
        context = t_context.extract_context_from_environ()
        pods = db_api.list_pods(context)
        for pod in pods:
            if not pod['az_name']:
                continue
            client = self._get_client(pod['pod_name'])
            extensions = client.list_extension(context)
            return extensions