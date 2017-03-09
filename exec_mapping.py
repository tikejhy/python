#!/usr/bin/env python

import argparse
import string
import re
import sys

class master(object):

 def __init__(self):
    self.parse_cli_args() 

 def parse_cli_args(self):
    ''' Command line argument processing '''

    import boto.ec2
    c = boto.ec2.connect_to_region('eu-west-1')
    reservations = c.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            if 'Name' in inst.tags:
                print "python mapping.py --host=%s" % (inst.tags['Name'])
            else:
                print "%s [%s]" % (inst.id, inst.state)

if __name__ == '__main__':
    # Run the script
    master()
