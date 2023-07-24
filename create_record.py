import json
import os
import logging
import requests
import errno
import configparser
from dotenv import load_dotenv
from datetime import date

def check_api_access(url, token):
    """
    Sends a GET request to test access to an api's endpoint
    If the token is invalid, an HTTPError exception with the status code 403 and the reason 'FORBIDDEN' is raised
    """
    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f'{url}/api/records?size=1',
        headers=request_headers,
        verify=True)

    # Raise an exception if there is an HTTP error
    response.raise_for_status()


def check_folder_exists(folder_path):
    """
    Raises an exception if the folder does not exist
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), folder_path)


def check_file_exists(file_path):
    """
    Raises an exception if the file does not exist
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)


def create_draft(url, token, metadata_file_path):
    """
    Creates a record, which remains private to its owner, from a file
    Raises an HTTPError exception if the request to create the record failed
    Returns the id of the newly created record
    """
    # Create the payload from the file (title, authors...)
    with open(metadata_file_path, 'r') as f:
        metadata = json.load(f)

    payload = json.dumps(metadata)

    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f'{url}/api/records',
        data=payload,
        headers=request_headers,
        verify=True)

    response.raise_for_status()

    record_url = response.json()['links']['record']
    record_id = record_url.split('/api/records/')[-1]
    return record_id


def get_data_files(input_folder_path, metadata_file):
    """
    Returns the filenames in the input folder, except for the metadata file
    """
    all_files = [item for item in os.listdir(input_folder_path) if os.path.isfile(os.path.join(input_folder_path, item))]
    data_files = [item for item in all_files if item != metadata_file]
    return data_files


def start_file_uploads(url, token, record_id, data_files):
    """
    Updates a record's metadata by specifying the files that should be attached to it
    Raises an HTTPError exception if the request to update the record failed
    """
    # Create the payload specifying the files to be attached to the record
    filename_vs_key = []

    for data_file in data_files:
        filename_vs_key.append({'key': data_file})

    payload = json.dumps(filename_vs_key)

    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f'{url}/api/records/{record_id}/draft/files',
        data=payload,
        headers=request_headers,
        verify=True)

    response.raise_for_status()


def upload_file_content(url, token, record_id, data_file_path, data_file):
    """
    Uploads a file's content
    Raises an HTTPError exception if the request to upload the file's content failed
    """
    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/octet-stream",
        "Authorization": f"Bearer {token}"
    }

    with open(data_file_path, 'rb') as f:
        response = requests.put(
            f'{url}/api/records/{record_id}/draft/files/{data_file}/content',
            data=f,
            headers=request_headers,
            verify=True
        )

    response.raise_for_status()


def complete_file_upload(url, token, record_id, data_file):
    """
    Completes the upload of a file's content
    Raises an HTTPError exception if the request to complete the upload of the file's content failed
    """
    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f'{url}/api/records/{record_id}/draft/files/{data_file}/commit',
        headers=request_headers,
        verify=True)

    response.raise_for_status()


def set_publication_date(url, token, record_id):
    """
    Sets the record's publication date to the current date in the record's metadata
    """
    metadata = get_draft_metadata(url, token, record_id)
    metadata['metadata']['publication_date'] = date.today().strftime('%Y-%m-%d')  # e.g., '2020-06-01'
    update_draft_metadata(url, token, record_id, metadata)


def get_draft_metadata(url, token, record_id):
    """
    Gets the metadata of a draft record
    Raises an HTTPError exception if the request to get the record's metadata failed
    """
    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{url}/api/records/{record_id}/draft",
        headers=request_headers,
        verify=True)

    response.raise_for_status()

    record_metadata = json.loads(response.text)
    return record_metadata


def update_draft_metadata(url, token, record_id, record_metadata):
    """
    Updates the record's metadata
    Raises an HTTPError exception if the request to update the record's metadata failed
    """
    payload = json.dumps(record_metadata)

    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Send PUT request
    response = requests.put(
        f'{url}/api/records/{record_id}/draft',
        data=payload,
        headers=request_headers,
        verify=True)

    response.raise_for_status()


def publish_draft(url, token, record_id):
    """
    Shares a draft with all users of the archive
    Raises an HTTPError exception if the request to share the draft failed
    """
    request_headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f'{url}/api/records/{record_id}/draft/actions/publish',
        headers=request_headers,
        verify=True)

    response.raise_for_status()


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    try:
        basedir = os.path.abspath(os.path.dirname(__file__))

        # Read configuration file config.ini
        config = configparser.ConfigParser()
        config.read(os.path.join(basedir, 'config.ini'))

        # Create environment variables from secrets.env
        load_dotenv(os.path.join(basedir, 'secrets.env'))
        logger.info('Environment variables created with success')

        select_main_archive = config.get('general', 'select_main_archive')

        if select_main_archive == 'True':
            url = config.get('general', 'main_archive_url')
            token = os.getenv('MAIN_ARCHIVE_TOKEN')
        elif select_main_archive == 'False':
            url = config.get('general', 'demo_archive_url')
            token = os.getenv('DEMO_ARCHIVE_TOKEN')
        else:
            raise Exception('Invalid value for select_main_archive in config.ini')

        # Make checks
        # - validity of token
        # - existence of input folder
        # - existence of input metadata file
        check_api_access(url, token)

        input_folder = config.get('create_and_share_first_version_of_record', 'input_folder')
        input_folder_path = os.path.join(basedir, input_folder)
        check_folder_exists(input_folder_path)
        logger.info('Input folder exists')

        initial_metadata_file = config.get('create_and_share_first_version_of_record', 'initial_metadata_file')
        initial_metadata_file_path = os.path.join(basedir, input_folder, initial_metadata_file)
        check_file_exists(initial_metadata_file_path)
        logger.info(f'Input file {initial_metadata_file} exists')

        # Create a draft on the archive from the content of initial_metadata_file
        # Get the id of the newly created record (e.g., 'cpbc8-ss975')
        record_id = create_draft(url, token, initial_metadata_file_path)
        logger.info(f'Draft record with id={record_id} created with success')

        # Update the record's metadata with the names of the data files that will be attached to the record
        # The data files are the files in the input folder, except for the initial metadata file
        data_files = get_data_files(input_folder_path, initial_metadata_file)
        start_file_uploads(url, token, record_id, data_files)
        logger.info('Data files specified with success')

        # For each data file, upload its content
        for file in data_files:
            file_path = os.path.join(basedir, input_folder, file)
            upload_file_content(url, token, record_id, file_path, file)
            complete_file_upload(url, token, record_id, file)

        logger.info('Data files uploaded with success')

        publish = config.get('create_and_share_first_version_of_record', 'publish')

        if publish == 'True':
            set_publication_date(url, token, record_id)
            logger.info('Publication date set with success')

            # Share the draft with all archive's users
            publish_draft(url, token, record_id)
            logger.info('Record published with success')

    except requests.exceptions.HTTPError as e:
        logger.error('Error occurred: ' + str(e))

        status_code = e.response.status_code
        reason = e.response.reason

        if status_code == 403 and reason == 'FORBIDDEN':
            logger.error('Check token\'s validity')

    except FileNotFoundError as e:
        logger.error('File not found: ' + str(e.filename))

    except Exception as e:
        logger.error('Error occurred: ' + str(e))