PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/avocado-virt
PROJECT=avocado-virt-tests
VERSION="0.1.0"

all:
	@echo "make check - Runs static checks in the source code"

check:
	selftests/checkall
