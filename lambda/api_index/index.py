import datetime
import os


def handler(event, context):
	now = datetime.datetime.now()
	return {
		"isBase64Encoded": True,
		"statusCode": 200,
		"stage": os.environ["STAGE"],
		"time": now.strftime("%X")
	}
