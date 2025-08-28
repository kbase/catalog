import json
import os

'''
Class responsible for parsing/validating the local function specs, processing the specs,
and returning something that can be saved to the DB.

Typical usage is to initialize and the read_and_validate.

Then, once a compilation report is made, you can perform a full validation.

Finally, to create entries for the db, you can call extract_lf_names and extract_lf_records


'''


class LocalFunctionReader:

    def __init__(self):
        self.function_specs = {}

    '''
    Quickly parses and validates that there are specs defined in the correct format in the
    correct version, and reads in everything.  If things looked ok, returns a simple report
    that can be used to print stuff to logs.
    '''

    def parse_and_basic_validation(self, basedir, module_details, module_name, version,
                                   git_commit_hash):

        report = {
            'n_local_functions': 0,
            'functions_parsed': [],
            'functions_errored': []
        }

        # 1) list files in ui/local_functions
        if os.path.isdir(os.path.join(basedir, 'ui', 'local_functions')):
            for spec in os.listdir(os.path.join(basedir, 'ui', 'local_functions')):
                if os.path.isfile(os.path.join(basedir, 'ui', 'local_functions', spec)):

                    file_name_tokens = spec.split('.')
                    if len(file_name_tokens) != 2:
                        continue
                    if file_name_tokens[1] == 'json':

                        # a spec is defined, so extract out the function id
                        function_id = file_name_tokens[0]

                        try:
                            with open(
                                    os.path.join(basedir, 'ui', 'local_functions', spec)) as file:
                                spec_parse = json.load(file)
                        except Exception as e:
                            report['functions_errored'].append({'filename': spec, 'error': str(e)})
                            continue

                        # make sure basic required fields are there
                        if 'name' not in spec_parse:
                            report['functions_errored'].append(
                                {'filename': spec,
                                 'error': "Local Function specification missing required field 'name'"})
                            continue
                        if not isinstance(spec_parse['name'], str):  # need to update for Python3
                            report['functions_errored'].append(
                                {'filename': spec,
                                 'error': "Local Function specification field 'name' must be a string"})
                            continue

                        if 'short_description' not in spec_parse:
                            report['functions_errored'].append(
                                {'filename': spec,
                                 'error': "Local Function specification missing required field 'short_description'"})
                            continue
                        if not isinstance(spec_parse['short_description'], str):
                            report['functions_errored'].append(
                                {'filename': spec,
                                 'error': "Local Function specification field 'short_description' must be a string"})
                            continue

                        if 'long_description' not in spec_parse:
                            report['functions_errored'].append(
                                {'filename': spec,
                                 'error': "Local Function specification missing required field 'long_description'"})
                            continue
                        long_description = spec_parse['long_description']

                        # right now authors should be optional, tags should be optional
                        authors = []
                        if 'authors' in spec_parse:
                            if self._validate_as_list_of_strings(spec_parse['authors']):
                                authors = spec_parse['authors']
                            else:
                                report['functions_errored'].append(
                                    {'filename': spec,
                                     'error': "Local Function specification optional field 'authors' must be a list of strings"})
                                continue
                        else:
                            # default authors to module owners
                            for o in module_details['owners']:
                                authors.append(o['kb_username'])

                        # could probably make this code cleaner, but for now just do brute force if/else to validate
                        tags = {'categories': [], 'input': {'file_types': [], 'kb_types': []},
                                'output': {'file_types': [], 'kb_types': []}}
                        if 'tags' in spec_parse:
                            if not isinstance(spec_parse['tags'], dict):
                                report['functions_errored'].append(
                                    {'filename': spec,
                                     'error': "Local Function specification optional field 'tags' must be an object"})
                                continue

                            if 'categories' in spec_parse:
                                if self._validate_as_list_of_strings(
                                        spec_parse['tags']['categories']):
                                    tags['categories'] = spec_parse['tags']['categories']
                                else:
                                    report['functions_errored'].append(
                                        {'filename': spec,
                                         'error': "Local Function specification optional field 'authors' must be a list of strings"})
                                    continue

                            if 'input' in spec_parse['tags']:
                                if not isinstance(spec_parse['tags']['input'], dict):
                                    report['functions_errored'].append(
                                        {'filename': spec,
                                         'error': "Local Function specification optional field 'tags.input' must be an object"})
                                    continue

                                if 'kb_types' in spec_parse['tags']['input']:
                                    if self._validate_as_list_of_strings(
                                            spec_parse['tags']['input']['kb_types']):
                                        tags['input']['kb_types'] = spec_parse['tags']['input'][
                                            'kb_types']
                                    else:
                                        report['functions_errored'].append(
                                            {'filename': spec,
                                             'error': "Local Function specification optional field 'tags.input.kb_types' must be a list of strings"})
                                        continue
                                if 'file_types' in spec_parse['tags']['input']:
                                    if self._validate_as_list_of_strings(
                                            spec_parse['tags']['input']['file_types']):
                                        tags['input']['file_types'] = spec_parse['tags']['input'][
                                            'file_types']
                                    else:
                                        report['functions_errored'].append(
                                            {'filename': spec,
                                             'error': "Local Function specification optional field 'tags.input.file_types' must be a list of strings"})
                                        continue
                            if 'output' in spec_parse['tags']:
                                if not isinstance(spec_parse['tags']['output'], dict):
                                    report['functions_errored'].append({'filename': spec,
                                                                        'error': "Local Function specification optional field 'tags.output' must be an object"})
                                    continue

                                if 'kb_types' in spec_parse['tags']['output']:
                                    if self._validate_as_list_of_strings(
                                            spec_parse['tags']['output']['kb_types']):
                                        tags['output']['kb_types'] = spec_parse['tags']['output'][
                                            'kb_types']
                                    else:
                                        report['functions_errored'].append(
                                            {'filename': spec,
                                             'error': "Local Function specification optional field 'tags.output.kb_types' must be a list of strings"})
                                        continue
                                if 'file_types' in spec_parse['tags']['output']:
                                    if self._validate_as_list_of_strings(
                                            spec_parse['tags']['output']['file_types']):
                                        tags['output']['file_types'] = \
                                        spec_parse['tags']['output']['file_types']
                                    else:
                                        report['functions_errored'].append(
                                            {'filename': spec,
                                             'error': "Local Function specification optional field 'tags.output.file_types' must be a list of strings"})
                                        continue

                        # handle case where long_description is a file
                        if os.path.isfile(
                                os.path.join(basedir, 'ui', 'local_functions', long_description)):
                            try:
                                with open(os.path.join(basedir, 'ui', 'local_functions',
                                                       long_description), 'r') as file:
                                    long_description = file.read()
                            except Exception as e:
                                report['functions_errored'].append(
                                    {'filename': spec,
                                     'error': "Unable to read file specified in long description: " + str(e)})
                                continue

                        function_data = {
                            'module_name': module_name,
                            'module_name_lc': module_name.lower(),
                            'function_id': function_id,
                            'version': version,
                            'git_commit_hash': git_commit_hash,
                            'name': spec_parse['name'],
                            'short_description': spec_parse['short_description'],
                            'long_description': long_description,
                            'authors': authors,
                            'tags': tags
                        }

                        self.function_specs[function_id] = function_data
                        report['functions_parsed'].append(function_id)
                        report['n_local_functions'] += 1
        return report

    def report_to_string_for_log(self, report):
        report_str = ''

        report_str += 'validating local function specifications\n'

        for r in report['functions_parsed']:
            report_str += '    - Valid spec: ui/local_functions/' + r + '.spec\n'

        for r in report['functions_errored']:
            report_str += '    - Error in ui/local_functions/' + r['filename'] + ':\n'
            report_str += '         ' + r['error'] + '\n'

        return report_str

    def _validate_as_list_of_strings(self, things):
        if not isinstance(things, list):
            return False
        for t in things:
            if not isinstance(t, str):
                return False
        return True

    def finish_validation(self, compilation_report):

        if len(self.function_specs) == 0:
            return

        if 'functions' not in compilation_report:
            raise ValueError('Invalid compilation report, functions are missing')
        if 'function_places' not in compilation_report:
            raise ValueError('Invalid compilation report, function_places are missing')

        # 1) compare functions to functions in the compilation report
        for fid in self.function_specs:
            if fid not in compilation_report['functions']:
                raise ValueError(
                    f'Invalid function specification, "{fid}" function could not be found. '
                    f'Check local function spec names.')
            if fid not in compilation_report['function_places']:
                raise ValueError(
                    f'Invalid function specification, "{fid}" function could not be found. '
                    f'Check local function spec names.')
            # 2) pull out documentation from the compilation report
            self.function_specs[fid]['kidl'] = {
                'parse': compilation_report['functions'][fid],
                'src_location': compilation_report['function_places'][fid]
            }

        return

    def extract_lf_names(self):
        return list(self.function_specs.keys())

    def extract_lf_records(self):
        return list(self.function_specs.values())
