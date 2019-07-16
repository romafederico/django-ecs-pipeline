import datetime
import boto3
import pymysql
import os
import unicodedata
import re
import random
import string
import uuid
from random import randint

env = os.environ['STAGE']
region = os.environ['AWS_REGION']
user_pool = os.environ['USER_POOL']
dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')
s3client = boto3.client('s3')
cognito = boto3.client('cognito-idp')
old_db = pymysql.connect(host="mysql.bukium.com", user="usr_prod", passwd="garreau", db="lb_prod", charset='utf8')
migration_table = dynamodb.Table('bukium-{}-migration'.format(env))
story_table = dynamodb.Table('bukium-{}-story'.format(env))
chapter_table = dynamodb.Table('bukium-{}-chapter'.format(env))
chapter_bucket = s3.Bucket('bukium-{}-{}-content'.format(env, region))


def clear_table(table, index):
    scan = table.scan(
        ProjectionExpression='#k',
        ExpressionAttributeNames={
            '#k': index
        }
    )

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key=each)


def clear_stories():
    old_content = s3client.list_objects_v2(
        Bucket='bukium-{}-{}-content'.format(env, region)
    )

    if 'Contents' in old_content:
        for item in old_content['Contents']:
            response = s3client.delete_object(
                Bucket='bukium-{}-{}-content'.format(env, region),
                Key=item["Key"]
            )

    clear_table(story_table, "story_id")
    clear_table(chapter_table, "chapter_id")


def handler(event, context):
    if env != 'production':
        clear_stories()

        users = (6966, 3984, 135, 24360, 15504, 24902)
        sql = """
            SELECT IdContenido, FechaAlta, IdUsuarioWeb, Titulo, Resumen, Imagen, Borrador, Creditos FROM NMW_Contenidos 
            WHERE IdUsuarioWeb in {};
        """.format(users)
    else:
        batch_size = 100
        user_count = 0 if not migration_table['last_user'] else migration_table['last_user']
        sql = """
			SELECT IdContenido, FechaAlta, IdUsuarioWeb, Titulo, Resumen, Imagen, Borrador, Creditos FROM NMW_Contenidos 
			WHERE IdUsuarioWeb >= {} AND IdUsuarioWeb < {};
		""".format(user_count, user_count + batch_size)

    try:
        with old_db.cursor() as cursor:

            cursor.execute(sql)
            result = cursor.fetchall()

            for story in result:
                try:
                    old_user_cursor = old_db.cursor()
                    old_user_cursor.execute("""
					    SELECT Email FROM NMW_Usuarios_Web
					    WHERE IdUsuarioWeb = {}
				    """.format(story[2]))
                    old_user_result = old_user_cursor.fetchall()
                    old_user_email = old_user_result[0][0] if old_user_result else None
                except Exception as e:
                    print('EXCEPTION STORY', e)

                try:
                    existing_user = cognito.list_users(
                        UserPoolId=user_pool,
                        Filter="email=\"{}\"".format(old_user_email)
                    )
                except Exception as e:
                    print('Exception EXSITING USER', e)

                try:
                    story_id = str(uuid.uuid1())
                    story_table.put_item(
                        Item={
                            "story_id": story_id,
                            "user_id": get_attribute_value(existing_user['Users'][0]['Attributes'], "sub"),
                            "title": fix_encoding(story[3]),
                            "summary": fix_encoding(story[4]) if story[4] else "...",
                            "cover": 'bukium_cover_{}{}.jpeg'.format(randint(0, 1), randint(0, 9)),
                            "is_published": True if story[6] == 2 else False,
                            "is_public": True,
                            "credits": story[7],
                            "created_at": int(story[1].timestamp())
                        }
                    )

                    sql = """
						SELECT IdContenido, NroCapitulo, Titulo, Contenido 
						FROM NMW_Contenidos_Capitulos
						WHERE IdContenido = {}
					""".format(story[0])
                    cursor.execute(sql)
                    results = cursor.fetchall()

                    for chapter in results:
                        chapter_id = str(uuid.uuid1())
                        try:
                            clean_chapter = strip_tags(fix_encoding(chapter[3]))
                        except Exception as e:
                            print(e)

                        try:
                            chapter_table.put_item(
                                Item={
                                    "chapter_id": chapter_id,
                                    "story_id": story_id,
                                    "chapter_number": chapter[1],
                                    "title": fix_encoding(chapter[2]) if chapter[2] else "Sin título",
                                    "is_public": True
                                }
                            )
                        except Exception as e:
                            print(story_id, " ---------- ", e)

                        try:
                            new_chapter = chapter_bucket.put_object(
                                Key="{}/{}".format(story_id, chapter_id),
                                Body=clean_chapter
                            )
                        except Exception as e:
                            print(e)

                except Exception as e:
                    print(e)

    except Exception as e:
        print(e)

invald_tags = ['a', 'b', 'i', 'u', 'img', 'div', 'span', 'table', 'tr', 'td', 'h1', 'h2', 'h3', 'h4', 'h5']


def fix_encoding(text):
    try:
        clean_text = text.encode('latin-1').decode('utf-8', 'replace')
        return clean_text
    except Exception:
        return text


def strip_tags(string):
    for tag in invald_tags:
        string = re.sub('<{}[^>]*?>'.format(tag), '', string)

    return string


def get_attribute_value(attributes, key):
    for attr in attributes:
        if attr['Name'] == key:
            return attr['Value']
