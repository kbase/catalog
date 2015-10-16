
import sys
from biokbase.catalog.Client import Catalog
from pprint import pprint


catalog = Catalog('http://localhost:5000',user_id='wstester1',password='Catfasta11')
catalogAdmin = Catalog('http://localhost:5000',user_id='wstester2',password='Catfasta22')

print(catalog.version())



#catalog.push_dev_to_beta({'module_name':'onerepotest'})
#sys.exit()

print(catalog.register_repo({'git_url':'https://github.com/kbaseIncubator/onerepotest'}))

while True:
    state = catalog.get_module_state({'git_url':'https://github.com/kbaseIncubator/onerepotest'})
    pprint(state)
    if state['registration'] in ['complete','error']:
        break

sys.exit()

sys.exit()


selection = {
                'git_url':'https://github.com/kbaseIncubator/contigcount'
            }
print(catalog.get_module_state(selection))


set_registration_params = {
                'git_url':'https://github.com/kbaseIncubator/contigcount',
                'registration_state':'complete'
            }
catalogAdmin.set_registration_state(set_registration_params)

print(catalog.get_module_state(selection))

print(catalog.is_registered(selection))
print(catalog.is_registered({}))

print("===== List Modules:")
pprint(catalog.list_basic_module_info({"include_disabled":0}))




catalog.request_release({'module_name':'onerepotest'})
#print("accepting")
catalogAdmin.review_release_request({'decision':'approved','module_name':'onerepotest'})

#print("===== List Requested Releases:")
#pprint(catalog.list_requested_releases())


#catalog.push_dev_to_beta({'git_url':'https://github.com/kbaseIncubator/contigcount'})
#catalog.request_release({'git_url':'https://github.com/kbaseIncubator/contigcount'})


print("===== List Requested Releases:")
pprint(catalog.list_requested_releases())