from __future__ import print_function

import boto3
import json
import logging
import os

from urllib2 import Request, urlopen, URLError, HTTPError

SLACK_CHANNEL = "#general"
HOOK_URL = "https://hooks.slack.com/services/xxxxxxxxxxx"
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    #dbg_message = str(event)            #shows unicode string
    #dbg_message = json.loads(event)     #"errorMessage": "expected string or buffer"
    dbg_message = json.dumps(event)      #takes an object and produces a string
    
    try:
        logger.info('1:')
        message = json.loads(event['Records'][0]['Sns']['Message'])
        
        alarm_name = message['AlarmName']
        new_state = message['NewStateValue']
        reason = message['NewStateReason']
        
        slack_message = {
                'channel': SLACK_CHANNEL,
                'text': "%s state is now %s: %s" % (alarm_name, new_state, reason)
            }
        alert(slack_message)
    except (KeyError, TypeError) as e:
        try:
            logger.info('2:')
            message =  str('User: ' + event['detail']['userIdentity']['userName'] + event['detail']['userIdentity']['arn'] + ' : Initiated : ' + event['detail']['eventName'])
            slack_message = {
                'channel': SLACK_CHANNEL,
                'text': message
            }
            alert(slack_message)
        except (KeyError, TypeError) as e:
            try:
                logger.info('3:')
                message =  str(event['detail']['eventDescription'][0]['latestDescription']  + "\n\n<https://phd.aws.amazon.com/phd/home?region=eu-west-1#/event-log?eventID=" + event['detail']['eventArn'] + "|Click here> for details.")
                slack_message = {
                    'channel': SLACK_CHANNEL,
                    'text': message
                }
                alert(slack_message)
            except (KeyError, TypeError) as e:            
                try:
                    logger.info('4:')
                    message =  str("AWS Instance ID:" + event['detail']['instance-id'] + "::" + event['detail']['state'])
                    slack_message = {
                        'channel': SLACK_CHANNEL,
                        'text': message
                    }
                    alert(slack_message)
                except (KeyError, TypeError) as e:
                    try:
                        logger.info('5:')
                        message =  str("Event Name:" + event['detail']['eventName'] + ": Event Type:" + event['detail']['eventType'] + ": User ARN:" + event['detail']['userIdentity']['sessionContext']['sessionIssuer']['arn'])
                        slack_message = {
                            'channel': SLACK_CHANNEL,
                            'text': message
                        }
                        alert(slack_message)
                    except (KeyError, TypeError) as e:
                    	slack_message = {
                			'channel': SLACK_CHANNEL,
                			'text': 'No rules matched :confused: \n\n Raw event:' + dbg_message
            			}
                    	alert(slack_message)    
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