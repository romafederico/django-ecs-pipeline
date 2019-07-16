import boto3
from boto3.dynamodb.conditions import Key
import os
import datetime

env = os.environ['STAGE']
region = os.environ['AWS_REGION']
dynamodb = boto3.resource('dynamodb')
story_table = dynamodb.Table('bukium-{}-story'.format(env))
chapter_table = dynamodb.Table('bukium-{}-chapter'.format(env))
s3 = boto3.resource('s3')


def get_story_chapters(story_id):
    story = story_table.get_item(
        Key={
            "story_id": story_id
        }
    )

    chapters = chapter_table.query(
        IndexName="story_id-index",
        KeyConditionExpression=Key('story_id').eq(story_id)
    )
    chapters['Items'] = sorted(chapters['Items'], key=lambda k: k['chapter_number'])

    for chapter in chapters['Items']:
        content_object = s3.Object("bukium-{}-{}-content".format(env, region), "{}/{}".format(chapter['story_id'], chapter['chapter_id']))
        chapter['content'] = content_object.get()['Body'].read().decode('utf-8')

    story['Item']['content'] = chapters['Items']

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
    return get_story_chapters(event['story_id'])
