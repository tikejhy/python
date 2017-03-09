#!/usr/bin/env python

import argparse
import string
import re
import sys

class master(object):

 def __init__(self):
    self.parse_cli_args() 
    self.strip_suffix()
    self.strip_prefix()
    self.strip_prefix_strings()
    self.strip_suffix_digit()
    self.strip_prefix_digit() 
    self.get_and_fix_all_tags()

 def parse_cli_args(self):
    ''' Command line argument processing '''
    parser = argparse.ArgumentParser(description='Produce shit')
    parser.add_argument('--host', action='store', dest='hosts', required=True,
                          help='Get all the variables about a specific instance')
    self.args = parser.parse_args()
    

 def strip_suffix(self):
    ''' Strip suffix to get subenv of hostname parsed '''
    in_arg = self.args.hosts
    sep = '-'
    stripSuffix_res = in_arg.split(sep, -1)[-1]
    return stripSuffix_res
   
 def strip_prefix(self):
    ''' strip prefix of hostname parsed '''
    in_arg = self.args.hosts
    sep = '-'
    stripPrefix_res = in_arg.rsplit(sep, 1)[0]
    return stripPrefix_res

 def strip_prefix_strings(self):
    ''' strip strings and get ID '''
    in_arg=self.strip_prefix()
    all=string.maketrans('','')
    nodigs=all.translate(all, string.digits)
    stripPrefixStrings_res=in_arg.translate(all, nodigs)
    return stripPrefixStrings_res
 
 def strip_suffix_digit(self):
    ''' strip digit and get Env '''
    in_arg=self.strip_suffix()
    stripSuffixdigit_res = re.sub(r'\d+', '', in_arg)
    if re.search("^dev", stripSuffixdigit_res, re.IGNORECASE):
       stripSuffixdigit_res="dev"
    if re.search("^uat", stripSuffixdigit_res, re.IGNORECASE):
       stripSuffixdigit_res="uat"
    if re.search("^stg", stripSuffixdigit_res, re.IGNORECASE):
       stripSuffixdigit_res="stg"
    if re.search("^prod", stripSuffixdigit_res, re.IGNORECASE):
       stripSuffixdigit_res="prod"
    return stripSuffixdigit_res
    
 def strip_prefix_digit(self):
    ''' strip digit and get Role '''
    in_arg=self.strip_prefix()
    stripPrefixdigit_res = re.sub(r'\d+', '', in_arg)
    return stripPrefixdigit_res

 def get_proj_name(self):
    ''' Map server to project '''
    in_arg=self.strip_prefix()
    getProjName_res = re.sub(r'\d+', '', in_arg)
    if re.search("^mgmt|^jenkins|^bamboo|^chef|^mail|^es$|^elk|^zabbix", getProjName_res, re.IGNORECASE):
       getProjName_res="admin"
    if re.search("^nfs|^nas|^redirect|^mail", getProjName_res, re.IGNORECASE):
       getProjName_res="common"
    return getProjName_res


 def get_and_fix_all_tags(self):
    node_name = self.args.hosts
    node_role=self.strip_prefix_digit()
    node_id=self.strip_prefix_strings()
    node_env=self.strip_suffix_digit()
    node_subenv=self.strip_suffix()
    node_proj=self.get_proj_name()
    
    import boto.ec2
    c = boto.ec2.connect_to_region('eu-west-1')
    reservations = c.get_all_reservations()
    for res in reservations:
        for inst in res.instances:
            if inst.tags['Name'] == node_name:
                t={'Env':node_env,'Subenv':node_subenv,'Proj':node_proj}
                for x in t.keys():
                    if x in inst.tags:
                        if inst.tags[x] == t[x]:
                            print x + ": %s Name: %s ID: (%s) State: [%s]" % (inst.tags[x], inst.tags['Name'], inst.id, inst.state)
                        else:
                            print "Hmmm: expected Value of KEY: " + x + " to have VALUE: " + t[x]
                            inst.remove_tag(x)
                            print "Lets fix it"
                            inst.add_tag(x, t[x])
                    else:
                        print "KEY: " + x + " needs updating for %s Instace id %s is in sate: [%s]" % (inst.tags['Name'], inst.id, inst.state)
                        inst.add_tag(x, t[x])


if __name__ == '__main__':
    # Run the script
    master()
