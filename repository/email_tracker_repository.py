import os
from datetime import datetime
from http import HTTPStatus
from typing import Tuple, Optional

from pynamodb.connection import Connection
from pynamodb.exceptions import (
    PutError,
    PynamoDBConnectionError,
    QueryError,
    TableDoesNotExist,
    TransactWriteError,
)
from pynamodb.transactions import TransactWrite

from constants.common_constants import EntryStatus
from model.email.email import EmailTracker, EmailTrackerIn
from repository.repository_utils import RepositoryUtils
from utils.logger import logger


class EmailTrackersRepository:
    """
    A repository class for managing email_tracker records in a DynamoDB table.

    This class provides methods for storing, querying, updating, and deleting email_tracker records.

    Attributes:
        core_obj (str): The core object name for email_tracker records.
        current_date (str): The current date and time in ISO format.
        conn (Connection): The PynamoDB connection for database operations.
    """

    def __init__(self) -> None:
        self.core_obj = 'EmailTracker'
        self.current_date = datetime.utcnow().isoformat()
        self.range_key = 'v0'
        self.conn = Connection(region=os.getenv('REGION'))
        self.latest_version = 0

    def query_email_tracker(self) -> Tuple[HTTPStatus, EmailTracker, str]:
        """
        Query email_tracker records from the database.

        Returns:
            Tuple[HTTPStatus, EmailTracker, str]: A tuple containing HTTP status, a email_tracker records,
            and an optional error message.
        """
        email_tracker_id = self.range_key
        try:
            email_tracker_entries = list(
                EmailTracker.query(
                    hash_key=self.core_obj,
                    range_key_condition=EmailTracker.rangeKey.__eq__(email_tracker_id),
                    filter_condition=EmailTracker.entryStatus == EntryStatus.ACTIVE.value,
                )
            )

            if not email_tracker_entries:
                message = f'EmailTracker with id {email_tracker_id} not found'
                logger.error(f'[{self.core_obj}={email_tracker_id}] {message}')

                return HTTPStatus.NOT_FOUND, None, message

        except QueryError as e:
            message = f'Failed to query email_tracker: {str(e)}'
            logger.error(f'[{self.core_obj} = {email_tracker_id}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        except TableDoesNotExist as db_error:
            message = f'Error on Table, Please check config to make sure table is created: {str(db_error)}'
            logger.error(f'[{self.core_obj} = {email_tracker_id}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        except PynamoDBConnectionError as db_error:
            message = f'Connection error occurred, Please check config(region, table name, etc): {str(db_error)}'
            logger.error(f'[{self.core_obj} = {email_tracker_id}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        else:
            logger.info(f'[{self.core_obj} = {email_tracker_id}]: Fetch EmailTracker data successful')
            return HTTPStatus.OK, email_tracker_entries[0], None

    def create_update_email_tracker(
        self, email_tracker_in: EmailTrackerIn, email_tracker_entry: Optional[EmailTracker] = None
    ) -> Tuple[HTTPStatus, EmailTracker, str]:
        """
        Update a email_tracker record in the database.

        Args:
            email_tracker_in (EmailTrackerIn): The new email_tracker data.
            email_tracker_entry (EmailTracker): The existing email_tracker record to be updated.

        Returns:
            Tuple[HTTPStatus, EmailTracker, str]: A tuple containing HTTP status, the updated email_tracker record,
            and an optional error message.
        """
        try:
            if email_tracker_entry is None:
                logger.info(f'[{self.core_obj}] ' f'Creating new email_tracker entry')
                email_tracker_entry = EmailTracker(
                    hash_key=self.core_obj,
                    rangeKey=self.range_key,
                    createDate=self.current_date,
                    updateDate=self.current_date,
                    createdBy=os.getenv('CURRENT_USER'),
                    updatedBy=os.getenv('CURRENT_USER'),
                    latestVersion=self.latest_version,
                    entryStatus=EntryStatus.ACTIVE.value,
                    entryId=str(self.latest_version),
                    lastEmailSent=email_tracker_in.lastEmailSent.isoformat(),
                    dailyEmailCount=email_tracker_in.dailyEmailCount,
                )
                email_tracker_entry.save()
                logger.info(f'[{email_tracker_entry.rangeKey}] ' f'Create event data succesful')

                return HTTPStatus.OK, email_tracker_entry, ''
            
            else:
                logger.info(f'[{self.core_obj}] ' f'Updating new email_tracker entry')
                data = RepositoryUtils.load_data(pydantic_schema_in=email_tracker_in, exclude_unset=True)
                has_update, updated_data = RepositoryUtils.get_update(
                    old_data=RepositoryUtils.db_model_to_dict(email_tracker_entry), new_data=data
                )
                if not has_update:
                    return HTTPStatus.OK, email_tracker_entry, 'No update'

                with TransactWrite(connection=self.conn) as transaction:
                    # Update Entry
                    updated_data.update(
                        updateDate=self.current_date,
                    )
                    actions = [getattr(EmailTracker, k).set(v) for k, v in updated_data.items()]
                    transaction.update(email_tracker_entry, actions=actions)

                email_tracker_entry.refresh()
                logger.info(f'[{email_tracker_entry.rangeKey}] ' f'Update event data succesful')

                return HTTPStatus.OK, email_tracker_entry, ''

        except PutError as e:
            message = f'Failed to save discount strategy form: {str(e)}'
            logger.error(f'[{self.core_obj}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        except TableDoesNotExist as db_error:
            message = f'Error on Table, Please check config to make sure table is created: {str(db_error)}'
            logger.error(f'[{self.core_obj}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        except PynamoDBConnectionError as db_error:
            message = f'Connection error occurred, Please check config(region, table name, etc): {str(db_error)}'
            logger.error(f'[{self.core_obj}]: {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message

        except TransactWriteError as e:
            message = f'Failed to update event data: {str(e)}'
            logger.error(f'[{email_tracker_entry.rangeKey}] {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, None, message


    def append_email_sent_count(self, email_tracker_entry: EmailTracker, append_count: int = 1):
        """Adds the dailyEmailSent attribute of the email_tracker_entry by append_count

        :param email_tracker_entry: The EmailTracker object to be updated.
        :type email_tracker_entry: EmailTracker

        :param append_count: The count to be appended.
        :type append_count: int

        :return: Tuple containing the HTTP status, the updated EmailTracker object, and a message.
        :rtype: Tuple[HTTPStatus, EmailTracker, str]

        """
        try:
            email_tracker_entry.update(actions=[EmailTracker.dailyEmailCount.add(append_count)])
            email_tracker_entry.save()

        except PutError as e:
            message = f'Failed to append daily email sent count: {str(e)}'
            logger.error(f'[{email_tracker_entry.rangeKey}] {message}')
            return HTTPStatus.INTERNAL_SERVER_ERROR, message

        else:
            logger.info(f'[{email_tracker_entry.rangeKey}] ' f'Update email data successful')
            return HTTPStatus.OK, email_tracker_entry, ''
                