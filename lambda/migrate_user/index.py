import boto3
import pymysql
import os
import unicodedata
import random
import string

users = (6966, 3984, 135, 24360, 15504, 24902)
env = os.environ['STAGE']
user_pool = os.environ['USER_POOL']
dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')
old_db = pymysql.connect(host="mysql.bukium.com", user="usr_prod", passwd="garreau", db="lb_prod", charset='utf8mb4')
country_table = dynamodb.Table('bukium-{}-country'.format(env))
migration_table = dynamodb.Table('bukium-{}-migration'.format(env))
user_profile_table = dynamodb.Table('bukium-{}-user-profile'.format(env))


def handler(event, context):
    try:
        with old_db.cursor() as cursor:
            sql = """
				SELECT ISO2, Nombre FROM NMW_Pais
				WHERE IdLang = 'ES';
			"""
            cursor.execute(sql)
            result = cursor.fetchall()
            for country in result:
                country_table.put_item(
                    Item={
                        'code': country[0],
                        'name': country[1]
                    })
        print('Imported Countries')
    except Exception as e:
        print(e)
        return

    if env != 'production':
        existing_users = cognito.list_users(
            UserPoolId=user_pool,
        )

        for user in existing_users['Users']:
            user_profile_table.delete_item(
                Key={"user_id": get_attribute_value(user['Attributes'], "sub")}
            )
            cognito.admin_delete_user(
                UserPoolId=user_pool,
                Username=user['Username']
            )

        print('Deleted all users and profiles')

        sql = """
			SELECT IdUsuarioWeb, Email, Clave, Nombre, Apellido, Pseudonimo, FechaNacimiento, Estado, Creditos, IdPais, FechaAlta, Imagen FROM NMW_Usuarios_Web 
			WHERE IdUsuarioWeb in {};
		""".format(users)
    else:
        batch_size = 500
        user_count = 0 if not migration_table['last_user'] else migration_table['last_user']
        sql = """
			SELECT IdUsuarioWeb, Email, Clave, Nombre, Apellido, Pseudonimo, FechaNacimiento, Estado, Creditos, IdPais, FechaAlta, Imagen FROM NMW_Usuarios_Web 
			WHERE IdUsuarioWeb >= {} AND IdUsuarioWeb < {};
		""".format(user_count, user_count + batch_size)

    try:
        with old_db.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            for user in result:
                username = user[1].replace("@", "")
                print('Starting with {}'.format(username))
                try:
                    print(user[5])
                    new_user = cognito.admin_create_user(
                        UserPoolId=user_pool,
                        Username=strip_accents(fix_encoding(user[5]).replace(" ", "")).lower(),
                        TemporaryPassword=user[2] if len(user[2]) > 5 else create_temporary_password(),
                        MessageAction="SUPPRESS",
                        UserAttributes=[
                            {
                                'Name': 'email',
                                'Value': user[1]
                            },
                            {
                                'Name': 'preferred_username',
                                'Value': strip_accents(fix_encoding(user[5]).replace(" ", "")).lower()
                            }
                        ]
                    )
                except Exception as e:
                    print(e)

                if user[9]:
                    country_cursor = old_db.cursor()
                    country_cursor.execute("""
							SELECT Nombre FROM NMW_Pais
							WHERE IdPais = {} 
							""".format(user[9]))
                    country_result = country_cursor.fetchall()
                    country_name = country_result[0][0] if country_result else None

                try:
                    user_profile_table.put_item(
                        Item={
                            "user_id": get_attribute_value(new_user['User']['Attributes'], "sub"),
                            "username": get_attribute_value(new_user['User']['Attributes'], "preferred_username"),
                            "first_name": fix_encoding(user[3]),
                            "last_name": fix_encoding(user[4]),
                            "date_of_birth": user[6].strftime("%s") if user[6] != "0000-00-00" else 0,
                            "credits": user[8],
                            "country": country_name if country_name else None,
                            "avatar": user[11] if user[11] else None
                        }
                    )
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)

    old_db.close()

def fix_encoding(text):
    return text.encode('latin-1').decode('utf-8', 'replace')


def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
        .decode("utf-8")

    return str(text)


def get_attribute_value(attributes, key):
    for attr in attributes:
        if attr['Name'] == key:
            return attr['Value']

def create_temporary_password(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
