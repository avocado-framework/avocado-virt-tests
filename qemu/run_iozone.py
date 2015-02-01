#!/usr/bin/python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>


from avocado.virt import test


class RunIOZoneTest(test.VirtTest):

    def action(self):
        self.vm.power_on()
        self.vm.login_remote()
        self.whiteboard = self.vm.remote.run('iozone -a').stdout

    def cleanup(self):
        if self.vm:
            if self.vm.remote:
                self.vm.remote.run('shutdown -h now')
                # TODO: Wait for machine to go down
            self.vm.power_off()

