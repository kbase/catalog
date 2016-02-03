#!/usr/bin/env python
from wsgiref.simple_server import make_server
import sys
import json
import traceback
import datetime
from multiprocessing import Process
from getopt import getopt, GetoptError
from jsonrpcbase import JSONRPCService, InvalidParamsError, KeywordError,\
    JSONRPCError, ServerError, InvalidRequestError
from os import environ
from ConfigParser import ConfigParser
from biokbase import log
import biokbase.nexus
import requests as _requests
import urlparse as _urlparse
import random as _random
import os

DEPLOY = 'KB_DEPLOYMENT_CONFIG'
SERVICE = 'KB_SERVICE_NAME'

# Note that the error fields do not match the 2.0 JSONRPC spec

def get_config_file():
    return environ.get(DEPLOY, None)


def get_service_name():
    return environ.get(SERVICE, None)


def get_config():
    if not get_config_file():
        return None
    retconfig = {}
    config = ConfigParser()
    config.read(get_config_file())
    for nameval in config.items(get_service_name() or 'Catalog'):
        retconfig[nameval[0]] = nameval[1]
    return retconfig

config = get_config()

from biokbase.catalog.Impl import Catalog
impl_Catalog = Catalog(config)


class JSONObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, frozenset):
            return list(obj)
        if hasattr(obj, 'toJSONable'):
            return obj.toJSONable()
        return json.JSONEncoder.default(self, obj)

sync_methods = {}
async_run_methods = {}
async_check_methods = {}
async_run_methods['Catalog.version_async'] = ['Catalog', 'version']
async_check_methods['Catalog.version_check'] = ['Catalog', 'version']
sync_methods['Catalog.version'] = True
async_run_methods['Catalog.is_registered_async'] = ['Catalog', 'is_registered']
async_check_methods['Catalog.is_registered_check'] = ['Catalog', 'is_registered']
sync_methods['Catalog.is_registered'] = True
async_run_methods['Catalog.register_repo_async'] = ['Catalog', 'register_repo']
async_check_methods['Catalog.register_repo_check'] = ['Catalog', 'register_repo']
sync_methods['Catalog.register_repo'] = True
async_run_methods['Catalog.push_dev_to_beta_async'] = ['Catalog', 'push_dev_to_beta']
async_check_methods['Catalog.push_dev_to_beta_check'] = ['Catalog', 'push_dev_to_beta']
sync_methods['Catalog.push_dev_to_beta'] = True
async_run_methods['Catalog.request_release_async'] = ['Catalog', 'request_release']
async_check_methods['Catalog.request_release_check'] = ['Catalog', 'request_release']
sync_methods['Catalog.request_release'] = True
async_run_methods['Catalog.list_requested_releases_async'] = ['Catalog', 'list_requested_releases']
async_check_methods['Catalog.list_requested_releases_check'] = ['Catalog', 'list_requested_releases']
sync_methods['Catalog.list_requested_releases'] = True
async_run_methods['Catalog.review_release_request_async'] = ['Catalog', 'review_release_request']
async_check_methods['Catalog.review_release_request_check'] = ['Catalog', 'review_release_request']
sync_methods['Catalog.review_release_request'] = True
async_run_methods['Catalog.list_basic_module_info_async'] = ['Catalog', 'list_basic_module_info']
async_check_methods['Catalog.list_basic_module_info_check'] = ['Catalog', 'list_basic_module_info']
sync_methods['Catalog.list_basic_module_info'] = True
async_run_methods['Catalog.add_favorite_async'] = ['Catalog', 'add_favorite']
async_check_methods['Catalog.add_favorite_check'] = ['Catalog', 'add_favorite']
sync_methods['Catalog.add_favorite'] = True
async_run_methods['Catalog.remove_favorite_async'] = ['Catalog', 'remove_favorite']
async_check_methods['Catalog.remove_favorite_check'] = ['Catalog', 'remove_favorite']
sync_methods['Catalog.remove_favorite'] = True
async_run_methods['Catalog.list_favorites_async'] = ['Catalog', 'list_favorites']
async_check_methods['Catalog.list_favorites_check'] = ['Catalog', 'list_favorites']
sync_methods['Catalog.list_favorites'] = True
async_run_methods['Catalog.list_app_favorites_async'] = ['Catalog', 'list_app_favorites']
async_check_methods['Catalog.list_app_favorites_check'] = ['Catalog', 'list_app_favorites']
sync_methods['Catalog.list_app_favorites'] = True
async_run_methods['Catalog.list_favorite_counts_async'] = ['Catalog', 'list_favorite_counts']
async_check_methods['Catalog.list_favorite_counts_check'] = ['Catalog', 'list_favorite_counts']
sync_methods['Catalog.list_favorite_counts'] = True
async_run_methods['Catalog.get_module_info_async'] = ['Catalog', 'get_module_info']
async_check_methods['Catalog.get_module_info_check'] = ['Catalog', 'get_module_info']
sync_methods['Catalog.get_module_info'] = True
async_run_methods['Catalog.get_version_info_async'] = ['Catalog', 'get_version_info']
async_check_methods['Catalog.get_version_info_check'] = ['Catalog', 'get_version_info']
sync_methods['Catalog.get_version_info'] = True
async_run_methods['Catalog.list_released_module_versions_async'] = ['Catalog', 'list_released_module_versions']
async_check_methods['Catalog.list_released_module_versions_check'] = ['Catalog', 'list_released_module_versions']
sync_methods['Catalog.list_released_module_versions'] = True
async_run_methods['Catalog.set_registration_state_async'] = ['Catalog', 'set_registration_state']
async_check_methods['Catalog.set_registration_state_check'] = ['Catalog', 'set_registration_state']
sync_methods['Catalog.set_registration_state'] = True
async_run_methods['Catalog.get_module_state_async'] = ['Catalog', 'get_module_state']
async_check_methods['Catalog.get_module_state_check'] = ['Catalog', 'get_module_state']
sync_methods['Catalog.get_module_state'] = True
async_run_methods['Catalog.get_build_log_async'] = ['Catalog', 'get_build_log']
async_check_methods['Catalog.get_build_log_check'] = ['Catalog', 'get_build_log']
sync_methods['Catalog.get_build_log'] = True
async_run_methods['Catalog.get_parsed_build_log_async'] = ['Catalog', 'get_parsed_build_log']
async_check_methods['Catalog.get_parsed_build_log_check'] = ['Catalog', 'get_parsed_build_log']
sync_methods['Catalog.get_parsed_build_log'] = True
async_run_methods['Catalog.list_builds_async'] = ['Catalog', 'list_builds']
async_check_methods['Catalog.list_builds_check'] = ['Catalog', 'list_builds']
sync_methods['Catalog.list_builds'] = True
async_run_methods['Catalog.delete_module_async'] = ['Catalog', 'delete_module']
async_check_methods['Catalog.delete_module_check'] = ['Catalog', 'delete_module']
sync_methods['Catalog.delete_module'] = True
async_run_methods['Catalog.migrate_module_to_new_git_url_async'] = ['Catalog', 'migrate_module_to_new_git_url']
async_check_methods['Catalog.migrate_module_to_new_git_url_check'] = ['Catalog', 'migrate_module_to_new_git_url']
sync_methods['Catalog.migrate_module_to_new_git_url'] = True
async_run_methods['Catalog.set_to_active_async'] = ['Catalog', 'set_to_active']
async_check_methods['Catalog.set_to_active_check'] = ['Catalog', 'set_to_active']
sync_methods['Catalog.set_to_active'] = True
async_run_methods['Catalog.set_to_inactive_async'] = ['Catalog', 'set_to_inactive']
async_check_methods['Catalog.set_to_inactive_check'] = ['Catalog', 'set_to_inactive']
sync_methods['Catalog.set_to_inactive'] = True
async_run_methods['Catalog.is_approved_developer_async'] = ['Catalog', 'is_approved_developer']
async_check_methods['Catalog.is_approved_developer_check'] = ['Catalog', 'is_approved_developer']
sync_methods['Catalog.is_approved_developer'] = True
async_run_methods['Catalog.list_approved_developers_async'] = ['Catalog', 'list_approved_developers']
async_check_methods['Catalog.list_approved_developers_check'] = ['Catalog', 'list_approved_developers']
sync_methods['Catalog.list_approved_developers'] = True
async_run_methods['Catalog.approve_developer_async'] = ['Catalog', 'approve_developer']
async_check_methods['Catalog.approve_developer_check'] = ['Catalog', 'approve_developer']
sync_methods['Catalog.approve_developer'] = True
async_run_methods['Catalog.revoke_developer_async'] = ['Catalog', 'revoke_developer']
async_check_methods['Catalog.revoke_developer_check'] = ['Catalog', 'revoke_developer']
sync_methods['Catalog.revoke_developer'] = True
async_run_methods['Catalog.log_exec_stats_async'] = ['Catalog', 'log_exec_stats']
async_check_methods['Catalog.log_exec_stats_check'] = ['Catalog', 'log_exec_stats']
sync_methods['Catalog.log_exec_stats'] = True
async_run_methods['Catalog.get_exec_aggr_stats_async'] = ['Catalog', 'get_exec_aggr_stats']
async_check_methods['Catalog.get_exec_aggr_stats_check'] = ['Catalog', 'get_exec_aggr_stats']
sync_methods['Catalog.get_exec_aggr_stats'] = True

class AsyncJobServiceClient(object):

    def __init__(self, timeout=30 * 60, token=None,
                 ignore_authrc=True, trust_all_ssl_certificates=False):
        url = environ.get('KB_JOB_SERVICE_URL', None)
        if url is None and config is not None:
            url = config.get('job-service-url')
        if url is None:
            raise ValueError('Neither \'job-service-url\' parameter is defined in '+
                    'configuration nor \'KB_JOB_SERVICE_URL\' variable is defined in system')
        scheme, _, _, _, _, _ = _urlparse.urlparse(url)
        if scheme not in ['http', 'https']:
            raise ValueError(url + " isn't a valid http url")
        self.url = url
        self.timeout = int(timeout)
        self._headers = dict()
        self.trust_all_ssl_certificates = trust_all_ssl_certificates
        if token is None:
            raise ValueError('Authentication is required for async methods')        
        self._headers['AUTHORIZATION'] = token
        if self.timeout < 1:
            raise ValueError('Timeout value must be at least 1 second')

    def _call(self, method, params, json_rpc_call_context = None):
        arg_hash = {'method': method,
                    'params': params,
                    'version': '1.1',
                    'id': str(_random.random())[2:]
                    }
        if json_rpc_call_context:
            arg_hash['context'] = json_rpc_call_context
        body = json.dumps(arg_hash, cls=JSONObjectEncoder)
        ret = _requests.post(self.url, data=body, headers=self._headers,
                             timeout=self.timeout,
                             verify=not self.trust_all_ssl_certificates)
        if ret.status_code == _requests.codes.server_error:
            if 'content-type' in ret.headers and ret.headers['content-type'] == 'application/json':
                err = json.loads(ret.text)
                if 'error' in err:
                    raise ServerError(**err['error'])
                else:
                    raise ServerError('Unknown', 0, ret.text)
            else:
                raise ServerError('Unknown', 0, ret.text)
        if ret.status_code != _requests.codes.OK:
            ret.raise_for_status()
        resp = json.loads(ret.text)
        if 'result' not in resp:
            raise ServerError('Unknown', 0, 'An unknown server error occurred')
        return resp['result']

    def run_job(self, run_job_params, json_rpc_call_context = None):
        return self._call('KBaseJobService.run_job', [run_job_params], json_rpc_call_context)[0]

    def check_job(self, job_id, json_rpc_call_context = None):
        return self._call('KBaseJobService.check_job', [job_id], json_rpc_call_context)[0]


class JSONRPCServiceCustom(JSONRPCService):

    def call(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in a JSON
        string or None if there is none.

        Arguments:
        jsondata -- remote method call in jsonrpc format
        """
        result = self.call_py(ctx, jsondata)
        if result is not None:
            return json.dumps(result, cls=JSONObjectEncoder)

        return None

    def _call_method(self, ctx, request):
        """Calls given method with given params and returns it value."""
        method = self.method_data[request['method']]['method']
        params = request['params']
        result = None
        try:
            if isinstance(params, list):
                # Does it have enough arguments?
                if len(params) < self._man_args(method) - 1:
                    raise InvalidParamsError('not enough arguments')
                # Does it have too many arguments?
                if(not self._vargs(method) and len(params) >
                        self._max_args(method) - 1):
                    raise InvalidParamsError('too many arguments')

                result = method(ctx, *params)
            elif isinstance(params, dict):
                # Do not accept keyword arguments if the jsonrpc version is
                # not >=1.1.
                if request['jsonrpc'] < 11:
                    raise KeywordError

                result = method(ctx, **params)
            else:  # No params
                result = method(ctx)
        except JSONRPCError:
            raise
        except Exception as e:
            # log.exception('method %s threw an exception' % request['method'])
            # Exception was raised inside the method.
            newerr = ServerError()
            newerr.trace = traceback.format_exc()
            newerr.data = e.__str__()
            raise newerr
        return result

    def call_py(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in python
        object format or None if there is none.

        This method is same as call() except the return value is a python
        object instead of JSON string. This method is mainly only useful for
        debugging purposes.
        """
        rdata = jsondata
        # we already deserialize the json string earlier in the server code, no
        # need to do it again
#        try:
#            rdata = json.loads(jsondata)
#        except ValueError:
#            raise ParseError

        # set some default values for error handling
        request = self._get_default_vals()

        if isinstance(rdata, dict) and rdata:
            # It's a single request.
            self._fill_request(request, rdata)
            respond = self._handle_request(ctx, request)

            # Don't respond to notifications
            if respond is None:
                return None

            return respond
        elif isinstance(rdata, list) and rdata:
            # It's a batch.
            requests = []
            responds = []

            for rdata_ in rdata:
                # set some default values for error handling
                request_ = self._get_default_vals()
                self._fill_request(request_, rdata_)
                requests.append(request_)

            for request_ in requests:
                respond = self._handle_request(ctx, request_)
                # Don't respond to notifications
                if respond is not None:
                    responds.append(respond)

            if responds:
                return responds

            # Nothing to respond.
            return None
        else:
            # empty dict, list or wrong type
            raise InvalidRequestError

    def _handle_request(self, ctx, request):
        """Handles given request and returns its response."""
        if self.method_data[request['method']].has_key('types'): # @IgnorePep8
            self._validate_params_types(request['method'], request['params'])

        result = self._call_method(ctx, request)

        # Do not respond to notifications.
        if request['id'] is None:
            return None

        respond = {}
        self._fill_ver(request['jsonrpc'], respond)
        respond['result'] = result
        respond['id'] = request['id']

        return respond


class MethodContext(dict):

    def __init__(self, logger):
        self['client_ip'] = None
        self['user_id'] = None
        self['authenticated'] = None
        self['token'] = None
        self['module'] = None
        self['method'] = None
        self['call_id'] = None
        self['rpc_context'] = None
        self['provenance'] = None
        self._debug_levels = set([7, 8, 9, 'DEBUG', 'DEBUG2', 'DEBUG3'])
        self._logger = logger

    def log_err(self, message):
        self._log(log.ERR, message)

    def log_info(self, message):
        self._log(log.INFO, message)

    def log_debug(self, message, level=1):
        if level in self._debug_levels:
            pass
        else:
            level = int(level)
            if level < 1 or level > 3:
                raise ValueError("Illegal log level: " + str(level))
            level = level + 6
        self._log(level, message)

    def set_log_level(self, level):
        self._logger.set_log_level(level)

    def get_log_level(self):
        return self._logger.get_log_level()

    def clear_log_level(self):
        self._logger.clear_user_log_level()

    def _log(self, level, message):
        self._logger.log_message(level, message, self['client_ip'],
                                 self['user_id'], self['module'],
                                 self['method'], self['call_id'])


def getIPAddress(environ):
    xFF = environ.get('HTTP_X_FORWARDED_FOR')
    realIP = environ.get('HTTP_X_REAL_IP')
    trustXHeaders = config is None or \
        config.get('dont_trust_x_ip_headers') != 'true'

    if (trustXHeaders):
        if (xFF):
            return xFF.split(',')[0].strip()
        if (realIP):
            return realIP.strip()
    return environ.get('REMOTE_ADDR')


class Application(object):
    # Wrap the wsgi handler in a class definition so that we can
    # do some initialization and avoid regenerating stuff over
    # and over

    def logcallback(self):
        self.serverlog.set_log_file(self.userlog.get_log_file())

    def log(self, level, context, message):
        self.serverlog.log_message(level, message, context['client_ip'],
                                   context['user_id'], context['module'],
                                   context['method'], context['call_id'])

    def __init__(self):
        submod = get_service_name() or 'Catalog'
        self.userlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, changecallback=self.logcallback,
            config=get_config_file())
        self.serverlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, logfile=self.userlog.get_log_file())
        self.serverlog.set_log_level(6)
        self.rpc_service = JSONRPCServiceCustom()
        self.method_authentication = dict()
        self.rpc_service.add(impl_Catalog.version,
                             name='Catalog.version',
                             types=[])
        self.method_authentication['Catalog.version'] = 'none'
        self.rpc_service.add(impl_Catalog.is_registered,
                             name='Catalog.is_registered',
                             types=[dict])
        self.method_authentication['Catalog.is_registered'] = 'none'
        self.rpc_service.add(impl_Catalog.register_repo,
                             name='Catalog.register_repo',
                             types=[dict])
        self.method_authentication['Catalog.register_repo'] = 'required'
        self.rpc_service.add(impl_Catalog.push_dev_to_beta,
                             name='Catalog.push_dev_to_beta',
                             types=[dict])
        self.method_authentication['Catalog.push_dev_to_beta'] = 'required'
        self.rpc_service.add(impl_Catalog.request_release,
                             name='Catalog.request_release',
                             types=[dict])
        self.method_authentication['Catalog.request_release'] = 'required'
        self.rpc_service.add(impl_Catalog.list_requested_releases,
                             name='Catalog.list_requested_releases',
                             types=[])
        self.method_authentication['Catalog.list_requested_releases'] = 'none'
        self.rpc_service.add(impl_Catalog.review_release_request,
                             name='Catalog.review_release_request',
                             types=[dict])
        self.method_authentication['Catalog.review_release_request'] = 'required'
        self.rpc_service.add(impl_Catalog.list_basic_module_info,
                             name='Catalog.list_basic_module_info',
                             types=[dict])
        self.method_authentication['Catalog.list_basic_module_info'] = 'none'
        self.rpc_service.add(impl_Catalog.add_favorite,
                             name='Catalog.add_favorite',
                             types=[dict])
        self.method_authentication['Catalog.add_favorite'] = 'required'
        self.rpc_service.add(impl_Catalog.remove_favorite,
                             name='Catalog.remove_favorite',
                             types=[dict])
        self.method_authentication['Catalog.remove_favorite'] = 'required'
        self.rpc_service.add(impl_Catalog.list_favorites,
                             name='Catalog.list_favorites',
                             types=[basestring])
        self.method_authentication['Catalog.list_favorites'] = 'none'
        self.rpc_service.add(impl_Catalog.list_app_favorites,
                             name='Catalog.list_app_favorites',
                             types=[dict])
        self.method_authentication['Catalog.list_app_favorites'] = 'none'
        self.rpc_service.add(impl_Catalog.list_favorite_counts,
                             name='Catalog.list_favorite_counts',
                             types=[dict])
        self.method_authentication['Catalog.list_favorite_counts'] = 'none'
        self.rpc_service.add(impl_Catalog.get_module_info,
                             name='Catalog.get_module_info',
                             types=[dict])
        self.method_authentication['Catalog.get_module_info'] = 'none'
        self.rpc_service.add(impl_Catalog.get_version_info,
                             name='Catalog.get_version_info',
                             types=[dict])
        self.method_authentication['Catalog.get_version_info'] = 'none'
        self.rpc_service.add(impl_Catalog.list_released_module_versions,
                             name='Catalog.list_released_module_versions',
                             types=[dict])
        self.method_authentication['Catalog.list_released_module_versions'] = 'none'
        self.rpc_service.add(impl_Catalog.set_registration_state,
                             name='Catalog.set_registration_state',
                             types=[dict])
        self.method_authentication['Catalog.set_registration_state'] = 'required'
        self.rpc_service.add(impl_Catalog.get_module_state,
                             name='Catalog.get_module_state',
                             types=[dict])
        self.method_authentication['Catalog.get_module_state'] = 'none'
        self.rpc_service.add(impl_Catalog.get_build_log,
                             name='Catalog.get_build_log',
                             types=[basestring])
        self.method_authentication['Catalog.get_build_log'] = 'none'
        self.rpc_service.add(impl_Catalog.get_parsed_build_log,
                             name='Catalog.get_parsed_build_log',
                             types=[dict])
        self.method_authentication['Catalog.get_parsed_build_log'] = 'none'
        self.rpc_service.add(impl_Catalog.list_builds,
                             name='Catalog.list_builds',
                             types=[dict])
        self.method_authentication['Catalog.list_builds'] = 'none'
        self.rpc_service.add(impl_Catalog.delete_module,
                             name='Catalog.delete_module',
                             types=[dict])
        self.method_authentication['Catalog.delete_module'] = 'required'
        self.rpc_service.add(impl_Catalog.migrate_module_to_new_git_url,
                             name='Catalog.migrate_module_to_new_git_url',
                             types=[dict])
        self.method_authentication['Catalog.migrate_module_to_new_git_url'] = 'required'
        self.rpc_service.add(impl_Catalog.set_to_active,
                             name='Catalog.set_to_active',
                             types=[dict])
        self.method_authentication['Catalog.set_to_active'] = 'required'
        self.rpc_service.add(impl_Catalog.set_to_inactive,
                             name='Catalog.set_to_inactive',
                             types=[dict])
        self.method_authentication['Catalog.set_to_inactive'] = 'required'
        self.rpc_service.add(impl_Catalog.is_approved_developer,
                             name='Catalog.is_approved_developer',
                             types=[list])
        self.method_authentication['Catalog.is_approved_developer'] = 'none'
        self.rpc_service.add(impl_Catalog.list_approved_developers,
                             name='Catalog.list_approved_developers',
                             types=[])
        self.method_authentication['Catalog.list_approved_developers'] = 'none'
        self.rpc_service.add(impl_Catalog.approve_developer,
                             name='Catalog.approve_developer',
                             types=[basestring])
        self.method_authentication['Catalog.approve_developer'] = 'required'
        self.rpc_service.add(impl_Catalog.revoke_developer,
                             name='Catalog.revoke_developer',
                             types=[basestring])
        self.method_authentication['Catalog.revoke_developer'] = 'required'
        self.rpc_service.add(impl_Catalog.log_exec_stats,
                             name='Catalog.log_exec_stats',
                             types=[dict])
        self.method_authentication['Catalog.log_exec_stats'] = 'required'
        self.rpc_service.add(impl_Catalog.get_exec_aggr_stats,
                             name='Catalog.get_exec_aggr_stats',
                             types=[dict])
        self.method_authentication['Catalog.get_exec_aggr_stats'] = 'none'
        self.auth_client = biokbase.nexus.Client(
            config={'server': 'nexus.api.globusonline.org',
                    'verify_ssl': True,
                    'client': None,
                    'client_secret': None})

    def __call__(self, environ, start_response):
        # Context object, equivalent to the perl impl CallContext
        ctx = MethodContext(self.userlog)
        ctx['client_ip'] = getIPAddress(environ)
        status = '500 Internal Server Error'

        try:
            body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            body_size = 0
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            # we basically do nothing and just return headers
            status = '200 OK'
            rpc_result = ""
        else:
            request_body = environ['wsgi.input'].read(body_size)
            try:
                req = json.loads(request_body)
            except ValueError as ve:
                err = {'error': {'code': -32700,
                                 'name': "Parse error",
                                 'message': str(ve),
                                 }
                       }
                rpc_result = self.process_error(err, ctx, {'version': '1.1'})
            else:
                ctx['module'], ctx['method'] = req['method'].split('.')
                ctx['call_id'] = req['id']
                ctx['rpc_context'] = {'call_stack': [{'time':self.now_in_utc(), 'method': req['method']}]}
                prov_action = {'service': ctx['module'], 'method': ctx['method'], 
                               'method_params': req['params']}
                ctx['provenance'] = [prov_action]
                try:
                    token = environ.get('HTTP_AUTHORIZATION')
                    # parse out the method being requested and check if it
                    # has an authentication requirement
                    method_name = req['method']
                    if method_name in async_run_methods:
                        method_name = async_run_methods[method_name][0] + "." + async_run_methods[method_name][1]
                    if method_name in async_check_methods:
                        method_name = async_check_methods[method_name][0] + "." + async_check_methods[method_name][1]
                    auth_req = self.method_authentication.get(method_name,
                                                              "none")
                    if auth_req != "none":
                        if token is None and auth_req == 'required':
                            err = ServerError()
                            err.data = "Authentication required for " + \
                                "Catalog but no authentication header was passed"
                            raise err
                        elif token is None and auth_req == 'optional':
                            pass
                        else:
                            try:
                                user, _, _ = \
                                    self.auth_client.validate_token(token)
                                ctx['user_id'] = user
                                ctx['authenticated'] = 1
                                ctx['token'] = token
                            except Exception, e:
                                if auth_req == 'required':
                                    err = ServerError()
                                    err.data = \
                                        "Token validation failed: %s" % e
                                    raise err
                    if (environ.get('HTTP_X_FORWARDED_FOR')):
                        self.log(log.INFO, ctx, 'X-Forwarded-For: ' +
                                 environ.get('HTTP_X_FORWARDED_FOR'))
                    method_name = req['method']
                    if method_name in async_run_methods or method_name in async_check_methods:
                        if method_name in async_run_methods:
                            orig_method_pair = async_run_methods[method_name]
                        else:
                            orig_method_pair = async_check_methods[method_name]
                        orig_method_name = orig_method_pair[0] + '.' + orig_method_pair[1]
                        if 'required' != self.method_authentication.get(orig_method_name, 'none'):
                            err = ServerError()
                            err.data = 'Async method ' + orig_method_name + ' should require ' + \
                                'authentication, but it has authentication level: ' + \
                                self.method_authentication.get(orig_method_name, 'none')
                            raise err
                        job_service_client = AsyncJobServiceClient(token = ctx['token'])
                        if method_name in async_run_methods:
                            run_job_params = {
                                'method': orig_method_name,
                                'params': req['params']}
                            if 'rpc_context' in ctx:
                                run_job_params['rpc_context'] = ctx['rpc_context']
                            job_id = job_service_client.run_job(run_job_params)
                            respond = {'version': '1.1', 'result': [job_id], 'id': req['id']}
                            rpc_result = json.dumps(respond, cls=JSONObjectEncoder)
                            status = '200 OK'
                        else:
                            job_id = req['params'][0]
                            job_state = job_service_client.check_job(job_id)
                            finished = job_state['finished']
                            if finished != 0 and 'error' in job_state and job_state['error'] is not None:
                                err = {'error': job_state['error']}
                                rpc_result = self.process_error(err, ctx, req, None)
                            else:
                                respond = {'version': '1.1', 'result': [job_state], 'id': req['id']}
                                rpc_result = json.dumps(respond, cls=JSONObjectEncoder)
                                status = '200 OK'
                    elif method_name in sync_methods or (method_name + '_async') not in async_run_methods:
                        self.log(log.INFO, ctx, 'start method')
                        rpc_result = self.rpc_service.call(ctx, req)
                        self.log(log.INFO, ctx, 'end method')
                        status = '200 OK'
                    else:
                        err = ServerError()
                        err.data = 'Method ' + method_name + ' cannot be run synchronously'
                        raise err
                except JSONRPCError as jre:
                    err = {'error': {'code': jre.code,
                                     'name': jre.message,
                                     'message': jre.data
                                     }
                           }
                    trace = jre.trace if hasattr(jre, 'trace') else None
                    rpc_result = self.process_error(err, ctx, req, trace)
                except Exception, e:
                    err = {'error': {'code': 0,
                                     'name': 'Unexpected Server Error',
                                     'message': 'An unexpected server error ' +
                                                'occurred',
                                     }
                           }
                    rpc_result = self.process_error(err, ctx, req,
                                                    traceback.format_exc())

        # print 'The request method was %s\n' % environ['REQUEST_METHOD']
        # print 'The environment dictionary is:\n%s\n' % pprint.pformat(environ) @IgnorePep8
        # print 'The request body was: %s' % request_body
        # print 'The result from the method call is:\n%s\n' % \
        #    pprint.pformat(rpc_result)

        if rpc_result:
            response_body = rpc_result
        else:
            response_body = ''

        response_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Headers', environ.get(
                'HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'authorization')),
            ('content-type', 'application/json'),
            ('content-length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]

    def process_error(self, error, context, request, trace=None):
        if trace:
            self.log(log.ERR, context, trace.split('\n')[0:-1])
        if 'id' in request:
            error['id'] = request['id']
        if 'version' in request:
            error['version'] = request['version']
            if 'error' not in error['error'] or error['error']['error'] is None:
                error['error']['error'] = trace
        elif 'jsonrpc' in request:
            error['jsonrpc'] = request['jsonrpc']
            error['error']['data'] = trace
        else:
            error['version'] = '1.0'
            error['error']['error'] = trace
        return json.dumps(error)

    def now_in_utc(self):
        # Taken from http://stackoverflow.com/questions/3401428/how-to-get-an-isoformat-datetime-string-including-the-default-timezone
        dtnow = datetime.datetime.now()
        dtutcnow = datetime.datetime.utcnow()
        delta = dtnow - dtutcnow
        hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
        return "%s%+02d:%02d" % (dtnow.isoformat(), hh, mm)

application = Application()

# This is the uwsgi application dictionary. On startup uwsgi will look
# for this dict and pull its configuration from here.
# This simply lists where to "mount" the application in the URL path
#
# This uwsgi module "magically" appears when running the app within
# uwsgi and is not available otherwise, so wrap an exception handler
# around it
#
# To run this server in uwsgi with 4 workers listening on port 9999 use:
# uwsgi -M -p 4 --http :9999 --wsgi-file _this_file_
# To run a using the single threaded python BaseHTTP service
# listening on port 9999 by default execute this file
#
try:
    import uwsgi
# Before we do anything with the application, see if the
# configs specify patching all std routines to be asynch
# *ONLY* use this if you are going to wrap the service in
# a wsgi container that has enabled gevent, such as
# uwsgi with the --gevent option
    if config is not None and config.get('gevent_monkeypatch_all', False):
        print "Monkeypatching std libraries for async"
        from gevent import monkey
        monkey.patch_all()
    uwsgi.applications = {
        '': application
        }
except ImportError:
    # Not available outside of wsgi, ignore
    pass

_proc = None


def start_server(host='localhost', port=0, newprocess=False):
    '''
    By default, will start the server on localhost on a system assigned port
    in the main thread. Excecution of the main thread will stay in the server
    main loop until interrupted. To run the server in a separate process, and
    thus allow the stop_server method to be called, set newprocess = True. This
    will also allow returning of the port number.'''

    global _proc
    if _proc:
        raise RuntimeError('server is already running')
    httpd = make_server(host, port, application)
    port = httpd.server_address[1]
    print "Listening on port %s" % port
    if newprocess:
        _proc = Process(target=httpd.serve_forever)
        _proc.daemon = True
        _proc.start()
    else:
        httpd.serve_forever()
    return port


def stop_server():
    global _proc
    _proc.terminate()
    _proc = None

def process_async_cli(input_file_path, output_file_path, token):
    exit_code = 0
    with open(input_file_path) as data_file:    
        req = json.load(data_file)
    if 'version' not in req:
        req['version'] = '1.1'
    if 'id' not in req: 
        req['id'] = str(_random.random())[2:]
    ctx = MethodContext(application.userlog)
    if token:
        user, _, _ = application.auth_client.validate_token(token)
        ctx['user_id'] = user
        ctx['authenticated'] = 1
        ctx['token'] = token
    if 'context' in req:
        ctx['rpc_context'] = req['context']
    ctx['CLI'] = 1
    ctx['module'], ctx['method'] = req['method'].split('.')
    prov_action = {'service': ctx['module'], 'method': ctx['method'], 
                   'method_params': req['params']}
    ctx['provenance'] = [prov_action]
    resp = None
    try:
        resp = application.rpc_service.call_py(ctx, req)
    except JSONRPCError as jre:
        trace = jre.trace if hasattr(jre, 'trace') else None
        resp = {'id': req['id'],
                'version': req['version'],
                'error': {'code': jre.code,
                          'name': jre.message,
                          'message': jre.data,
                          'error': trace}
               }
    except Exception, e:
        trace = traceback.format_exc()
        resp = {'id': req['id'],
                'version': req['version'],
                'error': {'code': 0,
                          'name': 'Unexpected Server Error',
                          'message': 'An unexpected server error occurred',
                          'error': trace}
               }
    if 'error' in resp:
        exit_code = 500
    with open(output_file_path, "w") as f:
        f.write(json.dumps(resp, cls=JSONObjectEncoder))
    return exit_code
    
if __name__ == "__main__":
    if len(sys.argv) >= 3 and len(sys.argv) <= 4 and os.path.isfile(sys.argv[1]):
        token = None
        if len(sys.argv) == 4:
            if os.path.isfile(sys.argv[3]):
                with open(sys.argv[3]) as token_file: 
                    token = token_file.read()
            else:
                token = sys.argv[3]
        sys.exit(process_async_cli(sys.argv[1], sys.argv[2], token))
    try:
        opts, args = getopt(sys.argv[1:], "", ["port=", "host="])
    except GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)
    port = 9999
    host = 'localhost'
    for o, a in opts:
        if o == '--port':
            port = int(a)
        elif o == '--host':
            host = a
            print "Host set to %s" % host
        else:
            assert False, "unhandled option"

    start_server(host=host, port=port)
#    print "Listening on port %s" % port
#    httpd = make_server( host, port, application)
#
#    httpd.serve_forever()
