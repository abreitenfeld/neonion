import requests
import logging
import json

from django.conf import settings
from requests.exceptions import ConnectionError

# Get an instance of a logger
logging.basicConfig()
logger = logging.getLogger('neonion.annotations.dispatcher')


def dispatch_annotation(method, annotation):
    if method.upper() in ['POST', 'PUT', 'DELETE']:
        if hasattr(settings, 'DISPATCHER_ENDPOINT'):
            headers = {}
            if hasattr(settings, 'DISPATCHER_SECRET_TOKEN'):
                # add secret token to header if provided
                headers['X-NEONION-TOKEN'] = settings.DISPATCHER_SECRET_TOKEN

            url = settings.DISPATCHER_ENDPOINT.rstrip('/') + '/annotations/'
            if method.upper() in ['PUT', 'DELETE']:
                # request on annotation object add id to url
                url += annotation['id']

            try:
                # do dispatch
                requests.request(method, url, data=json.dumps(annotation), headers=headers)
            except ConnectionError:
                logger.error("Dispatching " + method.upper() + " to " + url + " failed")
