#!/usr/bin/env python

import subprocess
import time
from runtime import *


class Device():
    # Class variable
    vendor = "google"

    def __init__(self, id, mode):
        # Instance variables
        self.id = id
        self.mode = mode
        # The below are for caching.
        self._rooted = None
        self._root_symbol = None
        self._magisk_version = None
        self._build = None
        self._hardware = None
        self._active_slot = None
        self._unlocked = None
        self._magisk_modules = None

    # ----------------------------------------------------------------------------
    #                               property root_symbol
    # ----------------------------------------------------------------------------
    @property
    def root_symbol(self):
        if self._root_symbol is None:
            if self.mode == 'f.b':
                self._root_symbol = '?'
            else:
                if self.rooted:
                    self._root_symbol = '✓'
                else:
                    self._root_symbol = '✗'
        return self._root_symbol

    # ----------------------------------------------------------------------------
    #                               property magisk_version
    # ----------------------------------------------------------------------------
    @property
    def magisk_version(self):
        if self._magisk_version is None:
            if self.mode == 'adb':
                if self.rooted:
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell \"su -c \'/data/adb/magisk/magisk32 -c\'\""
                    res = run_shell(theCmd)
                    if res.returncode == 0:
                        self._magisk_version = res.stdout
                else:
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell dumpsys package com.topjohnwu.mag | grep versionName"
                    res = run_shell(theCmd)
                    version = res.stdout.split('\n')
                    version = version[0].split('=')
                    try:
                        self._magisk_version = version[1]
                    except:
                        pass
        return self._magisk_version.strip('\n')

    # ----------------------------------------------------------------------------
    #                               property magisk_modules
    # ----------------------------------------------------------------------------
    @property
    def magisk_modules(self):
        if self._magisk_modules is None:
            if self.mode == 'adb':
                if self.rooted:
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell \"su -c \'ls /data/adb/modules\'\""
                    res = run_shell(theCmd)
                    if res.returncode == 0:
                        self._magisk_modules = res.stdout.split('\n')
                else:
                    self._magisk_modules = ''
        return self._magisk_modules

    # ----------------------------------------------------------------------------
    #                               property rooted
    # ----------------------------------------------------------------------------
    @property
    def rooted(self):
        if self._rooted is None:
            if self.mode == 'adb':
                if get_adb():
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell \"su -c \'ls -l /data/adb/magisk/\'\""
                    res = run_shell(theCmd)
                    if res.returncode == 0:
                        self._rooted = True
                    else:
                        self._rooted = False
                else:
                    print("\nERROR: adb command is not found!")
        return self._rooted

    # ----------------------------------------------------------------------------
    #                               property hardware
    # ----------------------------------------------------------------------------
    @property
    def hardware(self):
        if self._hardware is None:
            if self.mode == 'adb':
                if get_adb():
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell getprop ro.hardware"
                    hardware = run_shell(theCmd)
                    # remove any whitespace including tab and newline
                    self._hardware = ''.join(hardware.stdout.split())
                else:
                    print("\nERROR: adb command is not found!")
            elif self.mode == 'f.b':
                if get_fastboot():
                    theCmd = f"\"{get_fastboot()}\" -s {self.id} getvar product"
                    hardware = run_shell(theCmd)
                    # remove any whitespace including tab and newline
                    hardware = hardware.stderr.split('\n')
                    hardware = hardware[0].split(' ')
                    self._hardware = hardware[1]
                else:
                    print("\nERROR: fastboot command is not found!")
        return self._hardware

    # ----------------------------------------------------------------------------
    #                               property build
    # ----------------------------------------------------------------------------
    @property
    def build(self):
        if self._build is None:
            if self.mode == 'adb':
                if get_adb():
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell getprop ro.build.fingerprint"
                    fingerprint = run_shell(theCmd)
                    # remove any whitespace including tab and newline
                    fingerprint = ''.join(fingerprint.stdout.split())
                    self._build = fingerprint.split('/')[3]
                else:
                    print("\nERROR: adb command is not found!")
            else:
               self._build = ''
        return self._build

    # ----------------------------------------------------------------------------
    #                               property active_slot
    # ----------------------------------------------------------------------------
    @property
    def active_slot(self):
        if self._active_slot is None:
            if self.mode == 'adb':
                if get_adb():
                    theCmd = f"\"{get_adb()}\" -s {self.id} shell /bin/getprop ro.boot.slot_suffix"
                    active_slot = run_shell(theCmd)
                    if active_slot.returncode == 127:
                        theCmd = f"\"{get_adb()}\" -s {self.id} shell getprop ro.boot.slot_suffix"
                        active_slot = run_shell(theCmd)
                    active_slot = active_slot.stdout.replace("\n", "")
                    self._active_slot = active_slot.replace("_", "")
                else:
                    print("\nERROR: adb command is not found!")
            elif self.mode == 'f.b':
                if get_fastboot():
                    theCmd = f"\"{get_fastboot()}\" -s {self.id} getvar current-slot"
                    active_slot = run_shell(theCmd)
                    # remove any whitespace including tab and newline
                    active_slot = active_slot.stderr.split('\n')
                    active_slot = active_slot[0].split(' ')
                    self._active_slot = active_slot[1]
                else:
                    print("\nERROR: fastboot command is not found!")
        return self._active_slot

    # ----------------------------------------------------------------------------
    #                               property unlocked
    # ----------------------------------------------------------------------------
    @property
    def unlocked(self):
        if self._unlocked is None:
            if self.mode == 'f.b':
                if get_fastboot():
                    theCmd = f"\"{get_fastboot()}\" -s {self.id} getvar unlocked"
                    unlocked = run_shell(theCmd)
                    # remove any whitespace including tab and newline
                    unlocked = unlocked.stderr.split('\n')
                    unlocked = unlocked[0].split(' ')
                    unlocked = unlocked[1]
                    if unlocked == 'yes':
                        self._unlocked = True
                    else:
                        self._unlocked = False
                else:
                    print("\nERROR: fastboot command is not found!")
        return self._unlocked

    # ----------------------------------------------------------------------------
    #                               Method get_details
    # ----------------------------------------------------------------------------
    def get_device_details(self):
        details = "{:<3}({:<3})   {:<25}{:<12}{:<25}".format(self.root_symbol, self.mode, self.id, self.hardware, self.build)
        return details

    # ----------------------------------------------------------------------------
    #                               Method reboot_system
    # ----------------------------------------------------------------------------
    def reboot_system(self):
        print(f"Rebooting device {self.id} to system ...")
        if self.mode == 'adb' and get_adb():
            theCmd = f"\"{get_adb()}\" -s {self.id} reboot"
            debug(theCmd)
            res = run_shell(theCmd)
            return res
        elif self.mode == 'f.b' and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" -s {self.id} reboot"
            debug(theCmd)
            res = run_shell(theCmd)
            return res

    # ----------------------------------------------------------------------------
    #                               Method reboot_recovery
    # ----------------------------------------------------------------------------
    def reboot_recovery(self):
        print(f"Rebooting device {self.id} to recovery ...")
        if self.mode == 'adb' and get_adb():
            theCmd = f"\"{get_adb()}\" -s {self.id} reboot recovery "
            debug(theCmd)
            res = run_shell(theCmd)
            return res
        elif self.mode == 'f.b' and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" -s {self.id} reboot recovery"
            debug(theCmd)
            res = run_shell(theCmd)
            return res

    # ----------------------------------------------------------------------------
    #                               Method reboot_bootloader
    # ----------------------------------------------------------------------------
    def reboot_bootloader(self, fastboot_included = False):
        print(f"Rebooting device {self.id} to bootloader ...")
        if self.mode == 'adb' and get_adb():
            theCmd = f"\"{get_adb()}\" -s {self.id} reboot bootloader "
            debug(theCmd)
            res = run_shell(theCmd)
            return res
        elif self.mode == 'f.b' and fastboot_included and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" -s {self.id} reboot bootloader"
            debug(theCmd)
            res = run_shell(theCmd)
            return res

    # ----------------------------------------------------------------------------
    #                               Method reboot_fastbootd
    # ----------------------------------------------------------------------------
    def reboot_fastboot(self):
        print(f"Rebooting device {self.id} to fastbootd ...")
        print("This process will wait for fastbootd indefinitly.")
        print("WARNING! if your device does not boot to fastbootd PixelFlasher will hang and you'd have to kill it.")
        if self.mode == 'adb' and get_adb():
            theCmd = f"\"{get_adb()}\" -s {self.id} reboot fastboot "
            debug(theCmd)
            res = run_shell(theCmd)
            return res
        elif self.mode == 'f.b' and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" -s {self.id} reboot fastboot"
            debug(theCmd)
            res = run_shell(theCmd)
            return res

    # ----------------------------------------------------------------------------
    #                               Method set_active
    # ----------------------------------------------------------------------------
    def set_active_slot(self, slot):
        if self.mode == 'adb' and get_adb():
            self.reboot_bootloader()
            print("Waiting 5 seconds ...")
            time.sleep(5)
            phone.refresh_phone_mode()
        if self.mode == 'f.b' and get_fastboot():
            print(f"Setting active slot to slot [{slot}] for device {self.id} ...")
            theCmd = f"\"{get_fastboot()}\" -s {self.id} --set-active={slot}"
            debug(theCmd)
            res = run_shell(theCmd)
            return res

    # ----------------------------------------------------------------------------
    #                               Method disable_magisk_modules
    # ----------------------------------------------------------------------------
    def disable_magisk_modules(self):
        print("Disabling magisk modules device ...")
        if self.mode == 'adb' and get_adb():
            theCmd = f"\"{get_adb()}\" -s {self.id} wait-for-device shell magisk --remove-modules"
            debug(theCmd)
            res = run_shell(theCmd)
            return res
        elif self.mode == 'f.b' and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" -s {self.id} reboot reboot_system"
            debug(theCmd)
            res = run_shell(theCmd)
            print("Waiting 5 seconds ...")
            time.sleep(5)
            res = self.disable_magisk_modules(self)
            return res

    # ----------------------------------------------------------------------------
    #                               Method refresh_phone_info
    # ----------------------------------------------------------------------------
    def refresh_phone_mode(self):
        if self.mode == 'adb' and get_fastboot():
            theCmd = f"\"{get_fastboot()}\" devices"
            response = run_shell(theCmd)
            if self.id in response.stdout:
                self.mode = 'f.b'
        elif self.mode == 'f.b' and get_adb():
            theCmd = f"\"{get_adb()}\" devices"
            response = run_shell(theCmd)
            if self.id in response.stdout:
                self.mode = 'adb'


# ============================================================================
#                               Function run_shell
# ============================================================================
def run_shell(cmd):
    try:
        response = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return response
    except Exception as e:
        raise e


# ============================================================================
#                               Function debug
# ============================================================================
def debug(message):
    if get_verbose():
        print("debug: %s" % message)


# ============================================================================
#                               Function get_connected_devices
# ============================================================================
def get_connected_devices():
    devices = []
    phones = []

    if get_adb():
        theCmd = f"\"{get_adb()}\" devices"
        response = run_shell(theCmd)
        for device in response.stdout.split('\n'):
            if '\tdevice' in device:
                id = device.split("\t")
                id = id[0]
                device = Device(id, 'adb')
                device_details = device.get_device_details()
                devices.append(device_details)
                phones.append(device)
    else:
        print("\nERROR: adb command is not found!")

    if get_fastboot():
        theCmd = f"\"{get_fastboot()}\" devices"
        response = run_shell(theCmd)
        for device in response.stdout.split('\n'):
            if '\tfastboot' in device:
                id = device.split("\t")
                id = id[0]
                device = Device(id, 'f.b')
                device_details = device.get_device_details()
                devices.append(device_details)
                phones.append(device)
    else:
        print("\nERROR: fastboot command is not found!")

    set_phones(phones)
    return devices

