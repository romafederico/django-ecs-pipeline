import boto3
from boto3.dynamodb.conditions import Key
import os
import datetime

env = os.environ['STAGE']
dynamodb = boto3.resource('dynamodb')
user_profile_table = dynamodb.Table('bukium-{}-user-profile'.format(env))
story_table = dynamodb.Table('bukium-{}-story'.format(env))


def get_user_profile(username):
    user_profile = user_profile_table.query(
        IndexName='username-index',
        KeyConditionExpression=Key('username').eq(username)
    )

    user_stories = story_table.query(
        IndexName="user_id-index",
        KeyConditionExpression=Key('user_id').eq(user_profile['Items'][0]['user_id'])
    )

    user_profile['Items'][0]['stories'] = user_stories['Items']

    now = datetime.datetime.now()
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "stage": os.environ["STAGE"],
        "time": now.strftime("%X"),
        "body": user_profile['Items'][0]
    }
    return response


def handler(event, context):
    return get_user_profile(event['username'])
