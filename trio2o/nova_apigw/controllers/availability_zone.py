 # Copyright (c) 2017 VCCloud

import pecan
from pecan import expose, rest

import oslo_db.exception as db_exc

import trio2o.common.context as t_context
from trio2o.common.i18n import _
from trio2o.common import utils
from trio2o.db import api as db_api
from trio2o.db import core
from trio2o.db import models

def get_list_az(pods=[]):
    azs = []
    for pod in pods:
        if not pod['az_name']:
            continue
        if pod['az_name'] not in azs:
            azs.append(pod['az_name'])
    return azs

def get_az_info(pods, details=False):
    azs = get_list_az(pods)
    azs_info = []
    for az in azs:
        hosts = None
        # TO DO: query all service in a Pod and append to hosts
        # if details:
        #     for pod in pods:
        #         if pod['az_name'] == az:
        #             az_info['hosts'] 
        azs_info.append({'zoneName': az,
                         'hosts': hosts,
                         'zoneState': {
                             'available': True
                         }})
    return azs_info
    
class AvailabilityZoneController(rest.RestController):
    
    def __init__(self, project_id):
        self.project_id = project_id

    @expose(generic=True, template='json')
    def get(self):
        context = t_context.extract_context_from_environ()
        pods = db_api.list_pods(context)
        azs_info = get_az_info(pods)
        return {'availabilityZoneInfo': azs_info}

    @expose(generic=True, template='json')
    def get_one(self, _id):
        context = t_context.extract_context_from_environ()
        pods = db_api.list_pods(context)
        if _id == 'detail':
            azs_info = get_az_info(pods)
            return {'availabilityZoneInfo': azs_info}
        