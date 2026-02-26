import argparse
import os

import boto3
from botocore.exceptions import ClientError


class EmailServiceConfigAssembler:
    """
    Assembles the Email Service config file
    """

    def __init__(self, aws_region, environment):
        self.__input_environment = environment
        self.__project_name = 'sparcs-events'

        # Determine the deployment stage, defaulting to 'dev' for None or 'local' environments
        if not self.__input_environment or self.__input_environment == 'local':
            self.__stage = 'dev'
        else:
            self.__stage = self.__input_environment

        self.__region = 'ap-southeast-1'
        self.__ssm_client = boto3.client('ssm', region_name=self.__region)
        self.__secrets_client = boto3.client('secretsmanager', region_name=self.__region)
        self.__base_dir = os.getcwd()

    def __get_parameter(self, key, decrypt=False) -> str:
        """
        Retrieves parameter values from SSM

        :param key: key of parameter value to be retrieved
        :param decrypt: flag if value is decrypted
        :return: parameter value string
        """
        kwargs = {'Name': key, 'WithDecryption': decrypt}
        value = ''
        try:
            resp = self.__ssm_client.get_parameter(**kwargs)
        except ClientError as e:
            print(f'Error: {e.response["Error"]["Code"]} - {key}')
        else:
            value = resp['Parameter']['Value']
        return value

    def __get_secret(self, secret_arn) -> str:
        """
        Retrieves secret value from AWS Secrets Manager

        :param secret_arn: ARN of the secret to retrieve
        :return: secret value string
        """
        try:
            resp = self.__secrets_client.get_secret_value(SecretId=secret_arn)
            return resp['SecretString']
        except ClientError as e:
            print(f'Error retrieving secret: {e.response["Error"]["Code"]} - {secret_arn}')
            return ''

    @staticmethod
    def escape_env_value(value: str) -> str:
        return value.replace('$', '$$')

    @staticmethod
    def write_config(file_handle, key, value) -> None:
        """
        Writes specified config key-value in the config file

        :param file_handle: File pointer
        :param key: key of config
        :param value: value of config
        :return: None
        """
        entry = f'{key}={EmailServiceConfigAssembler.escape_env_value(str(value))}\n'
        file_handle.write(entry)

    def construct_config_file(self) -> None:
        """
        Constructs the config file for Email Service

        :return: None
        """
        stage = self.__stage
        parameter_store_prefix = '/techtix/'

        if self.__input_environment == 'test' or stage == 'test':
            # Placeholder for email service specific test values
            pass
        else:
            # Retrieve parameters from SSM Parameter Store for non-local environments
            pass

        config_file = f'{self.__base_dir}/.env'

        # Derived variables
        region = self.__region
        entities_table = f'{stage}-{self.__project_name}-entities'
        email_queue = f'{stage}-{self.__project_name}-email-queue.fifo'
        registrations_table = f'{stage}-{self.__project_name}-registrations'

        # Variables from SSM or placeholders
        sendgrid_api_key = ''
        frontend_url_dev = ''
        frontend_url_staging = ''
        frontend_url_prod = ''
        ses_smtp_username = ''
        ses_smtp_password = ''

        if self.__input_environment == 'test' or stage == 'test':
            sendgrid_api_key = 'dummy_sendgrid_key'  # nosec B105
            frontend_url_dev = 'http://localhost:3000'
            frontend_url_staging = 'http://localhost:3000'
            frontend_url_prod = 'http://localhost:3000'
            ses_smtp_username = 'dummy_ses_username'  # nosec B105
            ses_smtp_password = 'dummy_ses_password'  # nosec B105
        else:
            parameter_store_prefix = '/techtix'

            sendgrid_api_key = self.__get_parameter(
                f'{self.__stage}-{self.__project_name}-sendgrid-api-key', decrypt=True
            )
            frontend_url_dev = self.__get_parameter(f'{parameter_store_prefix}/frontend-url-dev', decrypt=False)
            frontend_url_staging = self.__get_parameter(f'{parameter_store_prefix}/frontend-url-staging', decrypt=False)
            frontend_url_prod = self.__get_parameter(f'{parameter_store_prefix}/frontend-url-prod', decrypt=False)
            ses_smtp_username = self.__get_parameter(f'{self.__project_name}-techtix-smtp-username', decrypt=True)
            ses_smtp_password = self.__get_parameter(f'{self.__project_name}-techtix-smtp-password', decrypt=True)

        with open(config_file, 'w', encoding='utf-8') as file_handle:
            self.write_config(file_handle, 'REGION', region)
            self.write_config(file_handle, 'STAGE', stage)
            self.write_config(file_handle, 'ENTITIES_TABLE', entities_table)
            self.write_config(file_handle, 'EMAIL_QUEUE', email_queue)
            self.write_config(file_handle, 'SENDGRID_API_KEY', sendgrid_api_key)
            self.write_config(file_handle, 'FRONTEND_URL_DEV', frontend_url_dev)
            self.write_config(file_handle, 'FRONTEND_URL_STAGING', frontend_url_staging)
            self.write_config(file_handle, 'FRONTEND_URL_PROD', frontend_url_prod)
            self.write_config(file_handle, 'REGISTRATIONS_TABLE', registrations_table)
            self.write_config(file_handle, 'SES_SMTP_USERNAME', ses_smtp_username)
            self.write_config(file_handle, 'SES_SMTP_PASSWORD', ses_smtp_password)

        print(f'Configuration file created successfully at: {config_file}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Email Service Configuration Assembler')
    parser.add_argument('-r', '--region', help='AWS Region (default: ap-southeast-1)')
    parser.add_argument('-s', '--stage', help='Environment Name (default: dev)')
    args = parser.parse_args()

    print('Arguments:', args)
    region = args.region
    input_stage = args.stage

    config_assembler = EmailServiceConfigAssembler(region, input_stage)
    config_assembler.construct_config_file()
