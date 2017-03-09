#!/usr/bin/env python

import argparse
import boto.ec2


class master(object):

 def __init__(self):
    ''' Main Execution Point '''
    self.parse_cli_args() 
    self.update_tags()

 def parse_cli_args(self):
    ''' Command line argument processing '''
    parser = argparse.ArgumentParser(description='Some shiny shit')
    parser.add_argument('--tag', action='store', dest='tag', required=True,
                          help='Tag name; Env, proj...')
    parser.add_argument('--task', action='store', dest='task', required=True,
                          help='Task can be remove or list')
    self.args = parser.parse_args()


 def list_tags(self):
    ''' Gets list of tags from entire region  '''
    ''' Mark parsed argument for tag into in_tag variable '''
    in_tag = self.args.tag
    ''' Mark parsed argument for task into in_task variable '''
    in_task = self.args.task
    c = boto.ec2.connect_to_region('eu-west-1')
    reservations = c.get_all_instances()
    
    ''' Loop through shit loads of reservation id's '''
    for res in reservations:
    ''' Loop through shit loads of instances '''
        for inst in res.instances:
    ''' Condition: If parsed Tag is matched '''
            if in_tag in inst.tags:
                print "%s (%s) [%s]" % (inst.tags[in_tag], inst.id, inst.state)
            else:
                print "---------"


 def update_tags(self):
    ''' Gets list of tags from entire region  '''
    ''' Mark parsed argument for tag into in_tag variable '''
    in_tag = self.args.tag
    ''' Mark parsed argument for task into in_task variable '''
    in_task = self.args.task
    c = boto.ec2.connect_to_region('eu-west-1')
    reservations = c.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            if in_task=="remove":
                print "Under Remove Task"
                if in_tag in inst.tags:
                   print "I can remove this tag for: %s %s (%s) [%s]" % (inst.tags['Name'], inst.tags[in_tag], inst.id, inst.state)
                   inst.remove_tag(in_tag)
                else:
                   print "Nothing in here %s (%s) [%s]" % (inst.tags['Name'], inst.id, inst.state)
            if in_task=="list":
                if in_tag in inst.tags:
                   print "%s %s (%s) [%s]" % (inst.tags[in_tag], inst.tags['Name'], inst.id, inst.state)

                else:
                    print "---------"


if __name__ == '__main__':
    # Run the script
    master()
