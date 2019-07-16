import boto3
from boto3.dynamodb.conditions import Key
import os
import datetime

env = os.environ['STAGE']
dynamodb = boto3.resource('dynamodb')
story_table = dynamodb.Table('bukium-{}-story'.format(env))
user_profile_table = dynamodb.Table('bukium-{}-user-profile'.format(env))


def get_story_profile(story_id):
    story = story_table.get_item(
        Key={
            "story_id": story_id
        }
    )

    user = user_profile_table.get_item(
        Key={
            "user_id": story['Item']['user_id']
        }
    )

    story['Item']['username'] = user['Item']['username']

    now = datetime.datetime.now()
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "stage": os.environ["STAGE"],
        "time": now.strftime("%X"),
        "body": story['Item']
    }
    return response


def handler(event, context):
    return get_story_profile(event['story_id'])
