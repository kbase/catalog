

# EDIT THESE BASED ON YOU ENV, todo: fix so this can run out of the catalog directory
export KB_TOP=/Users/msneddon/kb/deployment
export KB_RUNTIME=/Users/msneddon/kb/runtime/
export KB_SERVICE_DIR=/Users/msneddon/kb/deployment/services/catalog

export PYTHONPATH=$KB_TOP/lib:$PYTHONPATH
export PATH=$KB_TOP/bin:$KB_RUNTIME/bin:$PATH


python -m unittest discover -p "*_test.py"