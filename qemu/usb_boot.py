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


from avocado_virt import test
from avocado.core import exceptions


class USBBootTest(test.VirtTest):

    """
    Add a USB device to a QEMU vm and perform sanity checks on both QEMU monitor and guest OS.

    :param device_name: Expected name of the device in lsusb
    :param usb_bus_cmdline: Cmdline option to add the usb bus
    :param device_cmdline: Cmdline option to add the device
    :param check_cmd: Cmd to be ran in guest to query for the device_name
    :avocado: enable
    """
    device_name = None

    def setUp(self):
        """
        Add a USB device to a QEMU VM
        """
        super(USBBootTest, self).setUp()
        self.device_name = self.params.get('device_name',
                                           default='QEMU USB Tablet')
        usb_bus_cmdline = self.params.get('usb_bus_cmdline',
                                          default='-device piix3-usb-uhci,id=usbtest,bus=pci.0,addr=05')
        self.vm.devices.add_cmdline(usb_bus_cmdline)
        usb_device_cmdline = self.params.get('device_cmdline',
                                             default='-device usb-tablet,id=usb-tablet,bus=usbtest.0,port=1')
        self.vm.devices.add_cmdline(usb_device_cmdline)
        self.vm.power_on()
        self.vm.login_remote()
        self.vm.remote.run('dmesg -c')

    def check_io_errors(self):
        result_dmesg = self.vm.remote.run('dmesg')
        error_lines = []
        for line in result_dmesg.stdout.splitlines():
            if 'error' in line:
                error_lines.append(line)
        if error_lines:
            self.log.error('Errors found on dmesg')
            for line in error_lines:
                self.log.error(line)
            raise exceptions.TestFail('Errors found on guest dmesg')

    def test_shows_monitor(self):
        """
        Verify that the device shows up in QEMU monitor 'info usb' command.
        """
        args = {'command-line': 'info usb'}
        result_monitor = self.vm.qmp('human-monitor-command', **args)
        if self.device_name not in result_monitor['return']:
            raise exceptions.TestFail('Could not find %s in monitor info usb output' % self.device_name)
        self.check_io_errors()

    def test_shows_guest_os(self):
        """
        Verify that the device shows up in the guest OS.
        """
        check_cmd = self.params.get('check_cmd', default='lsusb -v')
        result_check = self.vm.remote.run(check_cmd)
        device_found = False
        for line in result_check.stdout.splitlines():
            if self.device_name in line:
                device_found = True
        if not device_found:
            raise exceptions.TestFail('Could not find %s in check command %s output' % (self.device_name, check_cmd))
        self.check_io_errors()

    def tearDown(self):
        if self.vm:
            self.vm.power_off()
