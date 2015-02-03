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
from avocado.core import exceptions

class USBBootTest(test.VirtTest):

    """
    1) Add a USB device to a QEMU VM
    2) Verify that the device shows up on 'info usb' monitor command
    3) Verify that the device shows up on 'lsusb -v' shell command
    4) Verify that there are no IO Errors showing on dmesg after
       2) and 3) are done.
    """

    def action(self):
        usb_bus_cmdline = self.params.get('virt.tests.usb_boot.usb_bus_cmdline',
                                          '-device piix3-usb-uhci,id=usbtest,bus=pci.0,addr=05')
        self.vm.devices.add_cmdline(usb_bus_cmdline)
        usb_device_cmdline = self.params.get('virt.tests.usb_boot.usb_device_cmdline',
                                             '-device usb-tablet,id=usb-tablet,bus=usbtest.0,port=1')
        self.vm.devices.add_cmdline(usb_device_cmdline)
        self.vm.power_on()
        self.vm.login_remote()

        check_cmd = self.params.get('virt.tests.usb_boot.check_cmd', 'lsusb -v')
        device_name = self.params.get('virt.tests.usb_boot.device_name', 'QEMU USB Tablet')

        failures = {'monitor': None, 'check_cmd': None, 'dmesg': None}

        # First, we have to clean the guest's dmesg
        self.vm.remote.run('dmesg -c')

        args = {'command-line': 'info usb'}
        result_monitor = self.vm.qmp('human-monitor-command', **args)
        if device_name not in result_monitor['return']:
            failures['monitor'] = 'Could not find %s in monitor info usb output' % device_name

        result_check = self.vm.remote.run(check_cmd)
        device_found = False
        for line in result_check.stdout.splitlines():
            if device_name in line:
                device_found = True
        if not device_found:
            failures['check_cmd'] = 'Could not find %s in %s output' % (device_name, check_cmd)

        # Now check it again, to see if we don't have IO Errors
        result_dmesg = self.vm.remote.run('dmesg -c')
        error_lines = []
        for line in result_dmesg.stdout.splitlines():
            if 'error' in line:
                error_lines.append(line)
        if error_lines:
            self.log.error('Errors found on dmesg')
            for line in error_lines:
                self.log.error(line)
            failures['dmesg'] = 'Errors found on guest dmesg'

        e_msg = []
        for key in failures:
            if failures[key] is not None:
                self.log.error(failures[key])
                e_msg.append(key)

        if e_msg:
            raise exceptions.TestFail('USB boot test found problems in: %s' % " ".join(e_msg))

    def cleanup(self):
        if self.vm:
            if self.vm.remote:
                self.vm.remote.run('shutdown -h now')
                # TODO: Wait for machine to go down
            self.vm.power_off()

