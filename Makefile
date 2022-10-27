include Makefile.common

PY_PACKAGE := ltpylib
PY_PATHS := $(PY_PACKAGE) $(PY_PACKAGE)tests

include Makefile.common-python

ci: lint test-parallel
