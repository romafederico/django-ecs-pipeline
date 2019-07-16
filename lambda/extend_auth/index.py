import boto3
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
cognito_identity_service_provider = boto3.client('cognito-idp')
lambda_client = boto3.client('lambda')


def handler(event, context):
	if event['RequestType'] == 'Create':
		print("-------------- CREATE --------------")
		try:
			try:
				domain = cognito_identity_service_provider.describe_user_pool_domain(
					Domain=event["ResourceProperties"]["Domain"]
				)
				response = cognito_identity_service_provider.delete_user_pool_domain(
					UserPoolId=domain["DomainDescription"]["UserPoolId"],
					Domain=event["ResourceProperties"]["Domain"]
				)
				print('delete_user_pool_domain', response)
			except Exception:
				pass
			response = lambda_client.update_function_configuration(
				FunctionName="arn:aws:lambda:{}:{}:function:{}-{}-migrate-user".format(
					event['ResourceProperties']['ProjectRegion'], event['ResourceProperties']['AccountId'],
					event['ResourceProperties']['BaseName'], event['ResourceProperties']['StageName']),
				Environment={
					"Variables": {
						"STAGE": event['ResourceProperties']['StageName'],
						"USER_POOL": event['ResourceProperties']['UserPoolId']
					}
				}
			)
			print('update_function_configuration_1', response)
			response = lambda_client.update_function_configuration(
				FunctionName="arn:aws:lambda:{}:{}:function:{}-{}-migrate-story".format(
					event['ResourceProperties']['ProjectRegion'], event['ResourceProperties']['AccountId'],
					event['ResourceProperties']['BaseName'], event['ResourceProperties']['StageName']),
				Environment={
					"Variables": {
						"STAGE": event['ResourceProperties']['StageName'],
						"USER_POOL": event['ResourceProperties']['UserPoolId']
					}
				}
			)
			print('update_function_configuration_2', response)
			response = cognito_identity_service_provider.create_identity_provider(
				UserPoolId=event['ResourceProperties']['UserPoolId'],
				ProviderName="Facebook",
				ProviderType="Facebook",
				ProviderDetails={
					'client_id': event['ResourceProperties']['FacebookAppId'],
					'client_secret': event['ResourceProperties']['FacebookAppSecret'],
					'authorize_scopes': 'public_profile,email'
				},
				AttributeMapping={
					'username': 'id',
					'email': 'email',
					'preferred_username': 'name'
				}
			)
			print('create_identity_provider', response)
			response = cognito_identity_service_provider.update_user_pool_client(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				ClientId=event["ResourceProperties"]["UserPoolClientId"],
				SupportedIdentityProviders=event["ResourceProperties"]["SupportedIdentityProviders"],
				ExplicitAuthFlows=event["ResourceProperties"]["ExplicitAuthFlows"],
				CallbackURLs=event["ResourceProperties"]["CallbackURL"],
				LogoutURLs=event["ResourceProperties"]["LogoutURL"],
				AllowedOAuthFlowsUserPoolClient=True,
				AllowedOAuthFlows=event["ResourceProperties"]["AllowedOAuthFlows"],
				AllowedOAuthScopes=event["ResourceProperties"]["AllowedOAuthScopes"]
			)
			print('update_user_pool_client', response)
			response = cognito_identity_service_provider.create_user_pool_domain(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				Domain=event["ResourceProperties"]["Domain"]
			)
			print('create_user_pool_domain', response)
		except Exception as e:
			logger.error("An error occured: {}".format(e))
			send_response("FAILED", event, context, {})

	if event['RequestType'] == 'Update':
		print("-------------- UPDATE --------------")
		try:
			try:
				domain = cognito_identity_service_provider.describe_user_pool_domain(
					Domain=event["ResourceProperties"]["Domain"]
				)
				response = cognito_identity_service_provider.delete_user_pool_domain(
					UserPoolId=domain["DomainDescription"]["UserPoolId"],
					Domain=event["ResourceProperties"]["Domain"]
				)
				print('delete_user_pool_domain', response)
			except Exception:
				pass
			response = lambda_client.update_function_configuration(
				FunctionName="arn:aws:lambda:{}:{}:function:{}-{}-migrate-user".format(
					event['ResourceProperties']['ProjectRegion'], event['ResourceProperties']['AccountId'],
					event['ResourceProperties']['BaseName'], event['ResourceProperties']['StageName']),
				Environment={
					"Variables": {
						"STAGE": event['ResourceProperties']['StageName'],
						"USER_POOL": event['ResourceProperties']['UserPoolId']
					}
				}
			)
			print('update_function_configuration_1', response)
			response = lambda_client.update_function_configuration(
				FunctionName="arn:aws:lambda:{}:{}:function:{}-{}-migrate-story".format(
					event['ResourceProperties']['ProjectRegion'], event['ResourceProperties']['AccountId'],
					event['ResourceProperties']['BaseName'], event['ResourceProperties']['StageName']),
				Environment={
					"Variables": {
						"STAGE": event['ResourceProperties']['StageName'],
						"USER_POOL": event['ResourceProperties']['UserPoolId']
					}
				}
			)
			print('update_function_configuration_2', response)
			try:
				response = cognito_identity_service_provider.update_identity_provider(
					UserPoolId=event['ResourceProperties']['UserPoolId'],
					ProviderName="Facebook",
					ProviderDetails={
						'client_id': event['ResourceProperties']['FacebookAppId'],
						'client_secret': event['ResourceProperties']['FacebookAppSecret'],
						'authorize_scopes': 'public_profile,email'
					},
					AttributeMapping={
						'username': 'id',
						'email': 'email',
						'preferred_username': 'name'
					}
				)
				print('update_identity_provider', response)
			except Exception:
				response = cognito_identity_service_provider.create_identity_provider(
					UserPoolId=event['ResourceProperties']['UserPoolId'],
					ProviderName="Facebook",
					ProviderType="Facebook",
					ProviderDetails={
						'client_id': event['ResourceProperties']['FacebookAppId'],
						'client_secret': event['ResourceProperties']['FacebookAppSecret'],
						'authorize_scopes': 'public_profile,email'
					},
					AttributeMapping={
						'username': 'id',
						'email': 'email',
						'preferred_username': 'name'
					}
				)
			print('create_identity_provider', response)
			response = cognito_identity_service_provider.update_user_pool_client(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				ClientId=event["ResourceProperties"]["UserPoolClientId"],
				SupportedIdentityProviders=event["ResourceProperties"]["SupportedIdentityProviders"],
				ExplicitAuthFlows=event["ResourceProperties"]["ExplicitAuthFlows"],
				CallbackURLs=event["ResourceProperties"]["CallbackURL"],
				LogoutURLs=event["ResourceProperties"]["LogoutURL"],
				AllowedOAuthFlowsUserPoolClient=True,
				AllowedOAuthFlows=event["ResourceProperties"]["AllowedOAuthFlows"],
				AllowedOAuthScopes=event["ResourceProperties"]["AllowedOAuthScopes"]
			)
			print('update_user_pool_client', response)
			response = cognito_identity_service_provider.create_user_pool_domain(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				Domain=event["ResourceProperties"]["Domain"]
			)
			print('create_user_pool_domain', response)
		except Exception as e:
			logger.error("An error occured: {}".format(e))
			send_response("FAILED", event, context, {})

	if event['RequestType'] == 'delete':
		try:
			response = cognito_identity_service_provider.delete_user_pool_domain(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				Domain=event["ResourceProperties"]["Domain"]
			)
			print('delete_user_pool_domain', response)
			response = cognito_identity_service_provider.delete_user_pool_client(
				UserPoolId=event["ResourceProperties"]["UserPoolId"],
				ClientId=event["ResourceProperties"]["UserPoolClientId"]
			)
			print('delete_user_pool_client', response)
			response = cognito_identity_service_provider.delete_identity_provider(
				UserPoolId=event['ResourceProperties']['UserPoolId'],
				ProviderName="Facebook"
			)
			print('delete_identity_provider', response)
		except Exception as e:
			logger.error("An error occured: {}".format(e))
			send_response("FAILED", event, context, {})

	send_response("SUCCESS", event, context, {})


def send_response(status, event, context, data):
	headers = {
		"Content-Type": ""
	}
	request_body = {
		"Status": status,
		"PhysicalResourceId" : context.log_stream_name,
		"StackId": event["StackId"],
		"RequestId": event["RequestId"],
		"LogicalResourceId": event["LogicalResourceId"],
		"Data": data
	}
	logger.debug(request_body)

	response = requests.put(event["ResponseURL"], headers=headers, data=json.dumps(request_body))
	logger.info("Response status code: {}".format(response.status_code))
