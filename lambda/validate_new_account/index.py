import os
import boto3

env = os.environ['STAGE']
dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')


def handler(event, context):
	print(event)

	if event['triggerSource'] == 'PreSignUp_ExternalProvider':
		new_user_email = event['request']['userAttributes']['email']
		print(new_user_email)
		try:
			existing_user = cognito.list_users(
				UserPoolId=event['userPoolId'],
				Filter="email=\"{}\"".format(new_user_email)
			)
			print("existing_user", existing_user)
		except Exception as e:
			print(e)
			return event

		for user in existing_user['Users']:
			for attr in user['Attributes']:
				print(attr['Name'], attr['Value'])
				if attr['Name'] == "email":
					event['request']['userAttributes']['email'] = attr['Value']

	return event
