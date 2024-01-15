import os
import warnings

import click
import requests

from big_map_archive_api_client.client.client_config import ClientConfig
from big_map_archive_api_client.utils import (create_directory,
                                              export_to_json_file,
                                              get_data_files_in_upload_dir)
from cli.root import cmd_root


@cmd_root.group('record')
@click.option(
    '--ignore',
    '-W',
    is_flag=True,
    help='Ignore warnings.'
)
def cmd_record(ignore):
    """
    Manage records on a BIG-MAP Archive.
    """
    # ignore warnings
    if ignore:
        warnings.filterwarnings('ignore')


@cmd_record.command('create')
@click.option(
    '--config-file',
    required=True,
    help='Path to the YAML file that specifies the domain name and a personal access token for the targeted BIG-MAP Archive. See bma_config.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--metadata-file',
    required=True,
    help='Path to the YAML file for the record\'s metadata (title, list of authors, etc). See data/input/example/create_record/metadata.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--data-files',
    required=True,
    help='Path to the directory that contains the data files to be uploaded and linked to the record. See data/input/example/create_record/upload in the GitHub repository.',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--publish',
    is_flag=True,
    help='Publish the created record.'
)
@click.option(
    '--slug',
    required=True,
    help='Community slug of the record. Example: for the BIG-MAP community the slug is bigmap.',
    type=click.STRING
)
def cmd_record_create(config_file,
                      metadata_file,
                      data_files,
                      publish,
                      slug):
    """
    Create a record on a BIG-MAP Archive and optionally publish it.
    """
    try:
        base_dir_path = os.getcwd()
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        # Get community id
        community_id = client.get_community_id(slug)

        # Create draft from input metadata.yaml
        response = client.post_records(base_dir_path, metadata_file)
        record_id = response['id']

        # Attribute draft to community
        response = client.put_draft_community(record_id, community_id)

        # Upload data files and insert links in the draft's metadata
        filenames = get_data_files_in_upload_dir(base_dir_path, data_files)

        if filenames != []:
            click.echo('Files are being uploaded...')
            client.upload_files(record_id, base_dir_path, data_files, filenames)
            click.echo('Files were uploaded.')
        click.echo('A new entry was created.')

        # Publish draft depending on user's choice
        if publish:
            client.insert_publication_date(record_id)
            client.post_review(record_id)
            click.echo('The entry was published.')
            click.echo(f'Please visit https://{client_config.domain_name}/records/{record_id}.')
            exit(0)

        click.echo(f'Please visit https://{client_config.domain_name}/uploads/{record_id}.')
    except requests.exceptions.ConnectionError as e:
        click.echo(f'An error of type ConnectionError occurred. Check the domain name in {config_file}. More info: {str(e)}.')
    except requests.exceptions.HTTPError as e:
        click.echo(f'An error of type HTTPError occurred. Check your token in {config_file}. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')


@cmd_record.command('get')
@click.option(
    '--config-file',
    required=True,
    help='Path to the YAML file that specifies the domain name and a personal access token for the targeted BIG-MAP Archive. See bma_config.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--record-id',
    required=True,
    help='Id of the published version of an archive entry (e.g., "pxrf9-zfh45").',
    type=str
)
@click.option(
    '--output-file',
    required=True,
    help='Path to the JSON file where the obtained record\'s metadata will be exported to.',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def cmd_record_get(config_file,
                   record_id,
                   output_file):
    """
    Get the metadata of a published version of an entry on a BIG-MAP Archive and save it to a file.
    """
    try:
        base_dir_path = os.getcwd()
        output_dir_path = os.path.dirname(output_file)
        create_directory(base_dir_path, output_dir_path)

        # Create an ArchiveAPIClient object to interact with the archive
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        response = client.get_record(record_id)

        export_to_json_file(base_dir_path, output_file, response)

        click.echo(f'The metadata of the entry version {record_id} was obtained and saved in {output_file}.')
    except requests.exceptions.ConnectionError as e:
        click.echo(f'An error of type ConnectionError occurred. Check the domain name in {config_file}. More info: {str(e)}.')
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 400:
            click.echo(f'An error of type HTTPError occurred. Check your token in {config_file}. More info: {str(e)}.')
        elif status_code == 404:
            click.echo(f'An error of type HTTPError occurred. Check your provided record id {record_id}. More info: {str(e)}.')
        else:
            click.echo(f'An error of type HTTPError occurred. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')


@cmd_record.command('get-all')
@click.option(
    '--config-file',
    required=True,
    help='Path to the YAML file that specifies the domain name and a personal access token for the targeted BIG-MAP Archive. See bma_config.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--all-versions',
    is_flag=True,
    help='Get all published versions for each entry. By default, only the latest published version for each entry is retrieved.'
)
@click.option(
    '--output-file',
    required=True,
    help='Path to the JSON file where the obtained record\'s metadata will be exported to.',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def cmd_record_get_all(config_file,
                       all_versions,
                       output_file):
    """
    Get the metadata of the latest published version for each entry on a BIG-MAP Archive and save them to a file.
    """
    try:
        base_dir_path = os.getcwd()
        output_dir_path = os.path.dirname(output_file)
        create_directory(base_dir_path, output_dir_path)

        # Create an ArchiveAPIClient object to interact with the archive
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        response_size = '1e6'
        response = client.get_records(all_versions, response_size)

        export_to_json_file(base_dir_path, output_file, response)

        click.echo(f'The metadata was obtained and saved in {output_file}.')
    except requests.exceptions.ConnectionError as e:
        click.echo(f'An error of type ConnectionError occurred. Check the domain name in {config_file}. More info: {str(e)}.')
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 400:
            click.echo(f'An error of type HTTPError occurred. Check your token in {config_file}. More info: {str(e)}.')
        else:
            click.echo(f'An error of type HTTPError occurred. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')


@cmd_record.command('update')
@click.option(
    '--config-file',
    required=True,
    help='Path to the YAML file that specifies the domain name and a personal access token for the targeted BIG-MAP Archive. See bma_config.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--record-id',
    required=True,
    help='Id of the published version (e.g., "pxrf9-zfh45").',
    type=str
)
@click.option(
    '--update-only',
    is_flag=True,
    help='Update the metadata of the published version, without creating a new version. By default, a new version is created.'
)
@click.option(
    '--metadata-file',
    required=True,
    help='Path to the YAML file that contains the metadata (title, list of authors, etc) for updating the published version or creating a new version. See data/input/example/update_record/metadata.yaml in the GitHub repository.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--data-files',
    required=True,
    help='Path to the directory that contains the data files to be linked to the newly created version. See data/input/example/update_record/upload in the GitHub repository.',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--link-all-files-from-previous',
    is_flag=True,
    help='Link all files that are already linked to the previous version to the new version, with the exception of files whose content changed.'
)
@click.option(
    '--publish',
    is_flag=True,
    help='Publish the newly created version.'
)
@click.option(
    '--slug',
    required=True,
    help='Community slug of the record. Example: for the BIG-MAP community the slug is bigmap.',
    type=click.STRING
)
def cmd_record_update(config_file,
                      record_id,
                      update_only,
                      metadata_file,
                      data_files,
                      link_all_files_from_previous,
                      publish,
                      slug):
    """
    Update a published version of an archive entry, or create a new version and optionally publish it. When updating a published version, only the metadata (title, list of authors, etc) can be modified.
    """
    try:
        base_dir_path = os.getcwd()
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        if update_only:
            # Create a draft (same version) and get the draft's id (same id)
            response = client.post_draft(record_id)
            record_id = response['id']  # Unchanged value for record_id

            # Update the draft's metadata
            client.update_metadata(record_id, base_dir_path, metadata_file)

            # Publish the draft (update published record)
            client.post_publish(record_id)

            click.echo(f'The metadata of the version {record_id} was updated.')
            click.echo(f'Please visit https://{client_config.domain_name}/records/{record_id}.')
        else:
            # Create a draft (new version) and get its id
            response = client.post_versions(record_id)
            record_id = response['id']  # Modified value for record_id

            # Update the draft's metadata
            client.update_metadata(record_id, base_dir_path, metadata_file)

            # Import all file links from the published version after cleaning
            filenames = client.get_links(record_id)
            client.delete_links(record_id, filenames)
            client.post_file_import(record_id)

            # Get a list of all file links to be removed and remove them
            filenames = client.get_links_to_delete(record_id, base_dir_path, data_files, link_all_files_from_previous)
            client.delete_links(record_id, filenames)

            # 5. Get a list of files to upload and upload them
            filenames = client.get_files_to_upload(record_id, base_dir_path, data_files)
            click.echo('Files are being uploaded...')
            client.upload_files(record_id, base_dir_path, data_files, filenames)
            click.echo('Files were uploaded.')

            click.echo('A new version was created.')

            # 6. Publish (optional)
            if publish:
                client.insert_publication_date(record_id)
                client.post_publish(record_id)

                click.echo('The new version was published.')
                click.echo(f'Please visit https://{client_config.domain_name}/records/{record_id}.')

                exit(0)

            click.echo(f'Please visit https://{client_config.domain_name}/uploads/{record_id}.')
    except requests.exceptions.ConnectionError as e:
        click.echo(f'An error of type ConnectionError occurred. Check the domain name in {config_file}. More info: {str(e)}.')
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 400:
            click.echo(f'An error of type HTTPError occurred. Check your token in {config_file}. More info: {str(e)}.')
        elif status_code == 404:
            click.echo(f'An error of type HTTPError occurred. Check your provided record id {record_id}. More info: {str(e)}.')
        else:
            click.echo(f'An error of type HTTPError occurred. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')
