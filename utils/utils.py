import logging
import os

from boto3.session import Session


class Utils:
    @staticmethod
    def get_secret(secret_name: str) -> str:
        secret = ''
        try:
            session = Session()
            client = session.client(service_name='ssm', region_name=os.getenv('REGION'))
            resp = client.get_parameter(Name=secret_name, WithDecryption=True)
            secret = resp['Parameter']['Value']
        except Exception as e:
            message = f'Failed to get secret, {secret_name}, from AWS SSM: {str(e)}'
            logging.error(message)

        return secret
