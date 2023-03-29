from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def create_auth_token():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        print("Token already exists")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return


def upload_basic(file_name: str, mimetype: str):
    """Insert new file.
    file_name - name of file need to upload
    mimetype - mime type of the file
    Returns : Id's of the file uploaded

    Load pre-authorized user credentials from the environment.
    """
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name,
                                mimetype=mimetype)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


def search_file(file_name):
    """Search file in drive location by its name
    Load pre-authorized user credentials from the environment.
    """
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(q="name='" + file_name + "'",
            fields="nextPageToken, files(id)").execute()
        items = results.get('files')
        if not items:
            print('No files found.')
            return False
        elif len(items) > 1:
            raise NameError("Several files found")
        return str(items[0]['id'])
    except HttpError as error:
        print(F'An error occurred: {error}')


def share_file(real_file_id, real_user):
    """Batch permission modification.
    Args:
        real_file_id: file Id
        real_user: User ID
        real_domain: Domain of the user ID
    Prints modified permissions
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        ids = []
        file_id = real_file_id

        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(exception)
            else:
                print(f'Request_Id: {request_id}')
                print(F'Permission Id: {response.get("id")}')
                ids.append(response.get('id'))

        # pylint: disable=maybe-no-member
        batch = service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': 'user@example.com'
        }
        # [START_EXCLUDE silent]
        user_permission['emailAddress'] = real_user
        # [END_EXCLUDE]
        batch.add(service.permissions().create(fileId=file_id,
                                               body=user_permission,
                                               fields='id',))
        # domain_permission = {
        #     'type': 'domain',
        #     'role': 'reader',
        #     'domain': 'example.com'
        # }
        # domain_permission['domain'] = real_domain
        # batch.add(service.permissions().create(fileId=file_id,
        #                                        body=domain_permission,
        #                                        fields='id',))
        batch.execute()

    except HttpError as error:
        print(F'An error occurred: {error}')
        ids = None

    return ids


def upload_revision(real_file_id, file_name, mimetype):
    """Replace the old file with new one on same file ID
    Args: ID of the file to be replaced
    Returns: file ID
    Load pre-authorized user credentials from the environment.
    """
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_id = real_file_id
        media = MediaFileUpload(file_name,
                                mimetype=mimetype,
                                resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().update(fileId=file_id,
                                      body={},
                                      media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')

    return file.get('id')
