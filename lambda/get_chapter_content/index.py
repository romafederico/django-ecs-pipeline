import boto3
from boto3.dynamodb.conditions import Key
import os
import datetime

env = os.environ['STAGE']
region = os.environ['AWS_REGION']
dynamodb = boto3.resource('dynamodb')
chapter_table = dynamodb.Table('bukium-{}-chapter'.format(env))
s3 = boto3.resource('s3')


def get_chapter_content(chapter_id):
    chapter = chapter_table.get_item(
        Key={
            "chapter_id": chapter_id
        }
    )

    content_object = s3.Object("bukium-{}-{}-content".format(env, region), "{}/{}".format(chapter['Item']['story_id'], chapter_id))
    chapter['Item']['content'] = content_object.get()['Body'].read().decode('utf-8')

    now = datetime.datetime.now()
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "stage": os.environ["STAGE"],
        "time": now.strftime("%X"),
        "body": chapter['Item']
    }
    return response


def handler(event, context):
    return get_chapter_content(event['chapter_id'])
