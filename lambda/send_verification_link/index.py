import boto3
import os

env = os.environ['STAGE']


def handler(event, context):
	client_id = event['callerContext']['clientId']
	username = event['userName']
	confirmation_code = event['request']['codeParameter']
	url = "https://{}.app.bukium.com/signup_success".format(env)
	link = "<a href=\"{}?client_id={}&user_name={}&confirmation_code={}\" target=\"_blank\">Click aqui</a>".format(url, client_id, username, confirmation_code)
	event['response']['emailMessage'] = "Link para activar cuenta - {}".format(link)
	return event
