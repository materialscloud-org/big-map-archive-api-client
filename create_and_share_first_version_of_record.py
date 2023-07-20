import json
import os
import logging
import requests
import errno


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
    Raises an HTTPError exception if the request to create the record fails
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
    Raises an HTTPError exception if the request to update the record fails
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
    Raises an HTTPError exception if the request to upload the file's content fails
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
    Raises an HTTPError exception if the request to complete the upload of the file's content fails
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

def publish_draft_record(url, token, record_id):
    """
    Shares a draft with all users of the archive
    Raises an HTTPError exception if the request to share the draft fails
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
    # -----------------Users: verify the information below-----------------
    # Specify the targeted archive:
    # - the main archive (main = True)
    # - the demo archive (main = False)
    main = False

    # Specify a valid token for the selected archive
    # If you need a new token, navigate to 'Applications' > 'Personal access tokens'
    #token = '<replace_with_token>'
    token = '6yIKqirBa91gnbn9M4Wo0RLOtRBc92OWdhgQQ0mIz9uRg9eswhQlsTtV4sk7'

    # Specify the folder where your input files are located
    input_folder = 'input'

    # Specify the file in the input folder that contains the title, the authors... for the record
    # Note that all other files in the input folder will automatically be attached to the record
    initial_metadata_file = 'initial_metadata.json'

    # Specify whether you wish to share the record with all archive's users
    publish = True

    # ---------------Users: do not modify the information below---------------
    # Archives' urls
    main_archive_url = 'https://archive.big-map.eu/'
    demo_archive_url = 'https://big-map-archive-demo.materialscloud.org/'
    url = demo_archive_url

    if main:
        url = main_archive_url

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    try:
        check_api_access(url, token)

        basedir = os.path.abspath(os.path.dirname(__file__))
        input_folder_path = os.path.join(basedir, input_folder)
        check_folder_exists(input_folder_path)
        logger.info('Input folder exists')

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
        for data_file in data_files:
            data_file_path = os.path.join(basedir, input_folder, data_file)
            upload_file_content(url, token, record_id, data_file_path, data_file)
            complete_file_upload(url, token, record_id, data_file)

        logger.info('Data files uploaded with success')

        if publish:
            # Share the draft with all archive's users
            publish_draft_record(url, token, record_id)
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