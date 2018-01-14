from __future__ import print_function

import boto3
import json
import logging
import os

from urllib2 import Request, urlopen, URLError, HTTPError

SLACK_CHANNEL       = os.environ['slackChannel']
HOOK_URL            = os.environ['HookUrl']
USER_NAME           = os.environ['project']
SLACK_ICON_EMOJI    = os.environ['emoji']
logger              = logging.getLogger()

logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    dbg_message = json.dumps(event)

    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])

        alarm_name = message['AlarmName']
        new_state = message['NewStateValue']
        reason = message['NewStateReason']
        
        slack_message = "%s state is now %s: %s" % (alarm_name, new_state, reason)
        
    except (KeyError, TypeError) as e:
        try:
            slack_message =  str('User: ' + event['detail']['userIdentity']['userName'] + event['detail']['userIdentity']['arn'] + ' : Initiated : ' + event['detail']['eventName'])
        except (KeyError, TypeError) as e:
            try:
                instance_id_from_event = str(event['detail']['instance-id'])
                instance_name_fetched = get_instance_name_by_id(instance_id_from_event)
                slack_message =  str("AWS Instance ID:  " + event['detail']['instance-id'] + " (" + instance_name_fetched + ") " + "  " + event['detail']['state'])
            except (KeyError, TypeError) as e:
                try:
                    latestDescription = event['detail']['eventDescription'][0]['latestDescription']
                    instance_id_from_event = event['resources']
                    all_instance_name_fetched = []
                    for idx, each_affected_instance_id in enumerate(instance_id_from_event):
                        instance_name_fetched = get_instance_name_by_id(each_affected_instance_id)
                        instance_id_name = str(instance_name_fetched + ' --> ' + each_affected_instance_id)
                        all_instance_name_fetched.append([instance_id_name])
                    slack_message =  str( event['detail']['eventDescription'][0]['latestDescription']  
                                        + "\n\n<https://phd.aws.amazon.com/phd/home?region=eu-west-1#/event-log?eventID=" 
                                        + event['detail']['eventArn'] 
                                        + "|Click here> for details." 
                                        + '\n \n' + 'Affected Resources: %s' %(all_instance_name_fetched))
                except (KeyError, TypeError) as e:
                    slack_message = 'No rules matched :confused: \n\n Raw event: %s' %(dbg_message)
                    
    slack_message_compose(slack_message, SLACK_CHANNEL, USER_NAME, SLACK_ICON_EMOJI)

def slack_message_compose(slack_message, slack_channel, slack_username, slack_icon_emoji):
        slack_message = {
              'channel': slack_channel,
              'username': slack_username,
              'text': slack_message,
              'icon_emoji': slack_icon_emoji
        }
        alert(slack_message)

def get_instance_name_by_id(fid):
    ec2 = boto3.resource('ec2')
    ec2instance = ec2.Instance(fid)
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename

def alert(slack_message):
    logger.info(str(slack_message))

    req = Request(HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
