import boto3
import os
import datetime

env = os.environ['STAGE']
dynamodb = boto3.client('dynamodb')
dynamodb_paginator = dynamodb.get_paginator('scan')
# story_table = dynamodb.Table('bukium-{}-story'.format(env))


def get_latest_stories():
    iterator = dynamodb_paginator.paginate(
        TableName='bukium-{}-story'.format(env),
        IndexName="created_at-index",
        PaginationConfig={
            "PageSize": 50
        }
    )

    print(iterator)
    now = datetime.datetime.now()
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "stage": os.environ["STAGE"],
        "time": now.strftime("%X"),
        "body": iterator['Item']
    }
    return response


def handler(event, context):
    return get_latest_stories()
