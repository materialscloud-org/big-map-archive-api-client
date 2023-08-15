from pathlib import Path
import os
from big_map_archive_api_client.client.client_config import ClientConfig
from big_map_archive_api_client.utils import (get_input_folder_files,
                                              export_to_json_file,
                                              export_capabilities_to_zip_file,
                                              group_results_by_tenant,
                                              get_archive_token)
from finales_api_client.client.client_config import FinalesClientConfig


def create_a_record(token,
                    input_dir='data/input',
                    metadata_filename='metadata.json',
                    publish=True):
    """
    Creates a record on a BIG-MAP Archive and, optionally, publishes it.

    :param token: personal access token for the archive
    :param input_dir: directory where input files (metadata file and data files) are located
    :param metadata_filename: name of the metadata file used for creating a record
    :param publish: whether the created record (draft) should be published or not
    :return: the id of the created record
    """
    base_dir = Path(__file__).absolute().parent.parent.parent
    config_file_path = os.path.join(base_dir, 'archive_config.yaml')
    client_config = ClientConfig.load_from_config_file(config_file_path)
    client = client_config.create_client(token)

    # Create draft from input metadata.json
    response = client.post_records(base_dir, input_dir, metadata_filename)
    record_id = response['id']

    # Upload data files and insert links in the draft's metadata
    filenames = get_input_folder_files(base_dir, input_dir, metadata_filename)
    client.upload_files(record_id, base_dir, input_dir, filenames)

    # Publish draft depending on user's choice
    if publish:
        client.insert_publication_date(record_id)
        client.post_publish(record_id)

    return record_id


def retrieve_a_published_record(token,
                                record_id,
                                export=True,
                                output_dir='data/output',
                                output_filename='metadata.json'):
    """
    Retrieves the metadata of a published record on a BIG-MAP Archive and, optionally, saves it to a file.

    :param token: personal access token for the archive
    :param record_id: id of the published record to retrieve
    :param export: whether the obtained metadata of the record should be saved to a file
    :param output_dir: directory where the output file is located
    :param output_filename: name of the output file
    """
    base_dir = Path(__file__).absolute().parent.parent.parent
    config_file_path = os.path.join(base_dir, 'archive_config.yaml')
    client_config = ClientConfig.load_from_config_file(config_file_path)
    client = client_config.create_client(token)
    response = client.get_record(record_id)

    if export:
        export_to_json_file(base_dir, output_dir, output_filename, response)


def retrieve_all_published_records(token,
                                   export=True,
                                   output_dir='data/output',
                                   output_filename='metadata.json',
                                   all_versions=False,
                                   response_size='1e6'):
    """
    Retrieves the metadata of all published records on a BIG-MAP Archive and, optionally, saves it to a file.

    :param token: personal access token for the archive
    :param export: whether the obtained metadata of the records should be saved to a file
    :param output_dir: directory where the output file is located
    :param output_filename: name of the output file
    :param all_versions: whether all record versions or only the latest record versions should be harvested
    :param response_size: maximum number of items in a response body
    """
    base_dir = Path(__file__).absolute().parent.parent.parent
    config_file_path = os.path.join(base_dir, 'archive_config.yaml')
    client_config = ClientConfig.load_from_config_file(config_file_path)
    client = client_config.create_client(token)

    response = client.get_records(all_versions, response_size)

    if export:
        export_to_json_file(base_dir, output_dir, output_filename, response)


def update_a_published_record(token,
                              record_id,
                              new_version=True,
                              input_dir='data/input',
                              metadata_filename='metadata.json',
                              force=True,
                              publish=True):
    """
    Updates a published record by either modifying the current version or creating a new version and, optionally, publishing it.

    :param token: personal access token for the archive
    :param record_id: id of the published record to update
    :param new_version: whether a new record version should be created
    :param input_dir: directory where input files (metadata file and data files) are located
    :param metadata_filename: name of the metadata file
    :param force: whether the new version should contain file links only for data files in the input folder
    (note that if such a file is already linked to the previous version, the link is simply imported, avoiding an extra upload)
    or the new version may also contain file links imported from the previous version for data files that do not appear in the input folder
    :param publish: whether the new version should be published
    :return: the id of the updated version or the new version
    """
    base_dir = Path(__file__).absolute().parent.parent.parent
    config_file_path = os.path.join(base_dir, 'archive_config.yaml')
    client_config = ClientConfig.load_from_config_file(config_file_path)
    client = client_config.create_client(token)

    if not new_version:
        # Create a draft (same version) and get the draft's id (same id)
        response = client.post_draft(record_id)
        record_id = response['id'] # Unchanged value for record_id

        # Update the draft's metadata
        client.update_metadata(record_id, base_dir, input_dir, metadata_filename)

        # Publish the draft (update published record)
        client.post_publish(record_id)
    else:
        # Create a draft (new version) and get its id
        response = client.post_versions(record_id)
        record_id = response['id'] # Modified value for record_id

        # Update the draft's metadata
        client.update_metadata(record_id, base_dir, input_dir, metadata_filename)

        # Import all file links from the previous version
        filenames = client.get_links(record_id)
        client.delete_links(record_id, filenames)
        client.post_file_import(record_id)

        # Get file links to remove and remove them
        filenames = client.get_links_to_delete(record_id, base_dir, input_dir, metadata_filename, force)
        client.delete_links(record_id, filenames)

        # Get list of files to upload and upload them
        filenames = client.get_files_to_upload(record_id, base_dir, input_dir, metadata_filename)
        client.upload_files(record_id, base_dir, input_dir, filenames)

        if publish:
            client.insert_publication_date(record_id)
            client.post_publish(record_id)

    return record_id
