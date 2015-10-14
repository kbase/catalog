

from biokbase.catalog.Client import Catalog
from pprint import pprint


catalog = Catalog('http://localhost:5000',user_id='wstester1',password='***')

print(catalog.version())

print(catalog.register_repo({'git_url':'https://github.com/kbaseIncubator/contigcount2'}))

selection = {
                'git_url':'https://github.com/kbaseIncubator/contigcount'
            }

print(catalog.get_module_state(selection))


set_registration_params = {
                'git_url':'https://github.com/kbaseIncubator/contigcount',
                'registration_state':'complete'
            }
catalog.set_registration_state(set_registration_params)

print(catalog.get_module_state(selection))

print(catalog.is_registered(selection))
print(catalog.is_registered({}))


pprint(catalog.list_basic_module_info({}))

