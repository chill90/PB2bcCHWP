import sys
import os

import argparse as ap
import src.chwp_control as cc

CC = cc.CHWP_Control()
#Command line arguments
allowed_commands = {'warmGrip': CC.warm_grip,
                    'cooldownGrip': CC.cooldown_grip,
                    'coldGrip': CC.cold_grip,
                    'coldUngrip': CC.cold_ungrip,
                    'gripperHome': CC.gripper_home,
                    'gripperReboot': CC.gripper_reboot}

parser = ap.ArgumentParser(description="Control program for the PB2bc CHWP")
parser.add_argument('command', choices=allowed_commands)

args = parser.parse_args()
func = allowed_commands[args.command]
func()
