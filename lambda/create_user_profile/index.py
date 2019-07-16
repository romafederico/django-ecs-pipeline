import boto3
import os

env = os.environ['STAGE']
dynamodb = boto3.resource('dynamodb')
user_profile_table = dynamodb.Table('bukium-{}-user-profile'.format(env))


def handler(event, context):

	user = event['request']['userAttributes']
	user_profile_table.put_item(
		Item={
			"user_id": user['sub']
		}
	)
	return event
