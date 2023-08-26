"""Commands to manage one record at a time."""
import click
from pathlib import Path
import os
import requests


from cli.root import cmd_root
from big_map_archive_api_client.client.client_config import ClientConfig
from big_map_archive_api_client.utils import (get_data_files_in_upload_dir,
                                              export_to_json_file,
                                              create_directory)


@cmd_root.group('record')
def cmd_record():
    """
    Deal with single records
    """

@cmd_record.command('create')
@click.option(
    '--config-file',
    show_default=True,
    default='bma_config.yaml',
    help='Relative path to the file specifying the domain name and a personal access token for the targeted BIG-MAP Archive.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--metadata-file',
    show_default=True,
    default='data/input/metadata.yaml',
    help='Relative path to the file for the record\'s metadata (title, list of authors, etc).',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--data-files',
    show_default=True,
    default='data/input/upload',
    help='Relative path to the data files to be uploaded and linked to the record.',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--publish',
    is_flag=True,
    help='Publish the created record.'
)
def cmd_record_create(config_file,
                      metadata_file,
                      data_files,
                      publish):
    """
    Create a record on a BIG-MAP Archive and optionally publish it.
    """
    try:
        base_dir_path = Path(__file__).absolute().parent.parent
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        # Create draft from input metadata.yaml
        response = client.post_records(base_dir_path, metadata_file, additional_description='')
        record_id = response['id']

        # Upload data files and insert links in the draft's metadata
        filenames = get_data_files_in_upload_dir(base_dir_path, data_files)
        client.upload_files(record_id, base_dir_path, data_files, filenames)

        click.echo('A new entry was created.')

        # Publish draft depending on user's choice
        if publish:
            client.insert_publication_date(record_id)
            client.post_publish(record_id)
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


@cmd_record.command('get-metadata')
@click.option(
    '--config-file',
    show_default=True,
    default='bma_config.yaml',
    help='Relative path to the file specifying the domain name and a personal access token for the targeted BIG-MAP Archive.',
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
    show_default=True,
    default='data/output/metadata.json',
    help='Relative path to the file where the obtained record\'s metadata will be exported to.',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def cmd_record_get_metadata(config_file,
                            record_id,
                            output_file):
    """
    Get the metadata of a published version of an entry on a BIG-MAP Archive and save it to a file.
    """
    try:
        base_dir_path = Path(__file__).absolute().parent.parent
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
        click.echo(f'An error of type HTTPError occurred. Check your token in {config_file}. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')


@cmd_record.command('update')
@click.option(
    '--config-file',
    show_default=True,
    default='bma_config.yaml',
    help='Relative path to the file specifying the domain name and a personal access token for the targeted BIG-MAP Archive.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--record-id',
    required=True,
    help='Id of the published version (e.g., "pxrf9-zfh45").',
    type=str
)
@click.option(
    '--update-version',
    is_flag=True,
    help='Update the metadata of the published version. By default, a new version is created.'
)
@click.option(
    '--metadata-file',
    show_default=True,
    default='data/input/metadata.yaml',
    help='Relative path to the file that contains the metadata (title, list of authors, etc) for updating the published version or creating a new version.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--data-files',
    show_default=True,
    default='data/input/upload',
    help='Relative path to the data files to be linked to the newly created version.',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--import-links',
    is_flag=True,
    help='Import file links from the published version into the newly created version, except for the files whose content was changed.'
)
@click.option(
    '--publish',
    is_flag=True,
    help='Publish the newly created version.'
)
def cmd_record_update(config_file,
                      record_id,
                      update_version,
                      metadata_file,
                      data_files,
                      import_links,
                      publish):
    """
    Update a published version of an archive entry, or create a new version and optionally publish it. When updating a published version, only the metadata (title, list of authors, etc) can be modified.
    """
    try:
        base_dir_path = Path(__file__).absolute().parent.parent
        config_file_path = os.path.join(base_dir_path, config_file)
        client_config = ClientConfig.load_from_config_file(config_file_path)
        client = client_config.create_client()

        if update_version:
            # Create a draft (same version) and get the draft's id (same id)
            response = client.post_draft(record_id)
            record_id = response['id']  # Unchanged value for record_id

            # Update the draft's metadata
            client.update_metadata(record_id, base_dir_path, metadata_file, additional_description='')

            # Publish the draft (update published record)
            client.post_publish(record_id)

            click.echo(f'The metadata of the version {record_id} was updated.')
            click.echo(f'Please visit https://{client_config.domain_name}/records/{record_id}.')
        else:
            # Create a draft (new version) and get its id
            response = client.post_versions(record_id)
            record_id = response['id']  # Modified value for record_id

            # Update the draft's metadata
            client.update_metadata(record_id, base_dir_path, metadata_file, additional_description='')

            # Import all file links from the published version after cleaning
            filenames = client.get_links(record_id)
            client.delete_links(record_id, filenames)
            client.post_file_import(record_id)

            # Get a list of all file links to be removed and remove them
            filenames = client.get_links_to_delete(record_id, base_dir_path, data_files, import_links)
            client.delete_links(record_id, filenames)

            # 5. Get a list of files to upload and upload them
            filenames = client.get_files_to_upload(record_id, base_dir_path, data_files)
            client.upload_files(record_id, base_dir_path, data_files, filenames)

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
            click.echo(f'An error of type HTTPError occurred. Check your provided record_id {record_id}. More info: {str(e)}.')
        else:
            click.echo(f'An error of type HTTPError occurred. More info: {str(e)}.')
    except Exception as e:
        click.echo(f'An error occurred. More info: {str(e)}.')