import datetime
import hashlib
import json
import os
import shutil

import yaml


def generate_full_metadata(base_dir_path, metadata_file_path):
    """
    Generates a record's full metadata from a YAML file containing only partial metadata
    """
    full_metadata = {
        'access': {
            'files': 'restricted',
            'record': 'restricted',
            "embargo": {
                "until": None,
                "active": False,
                "reason": None
            },
            'status': 'restricted'
        },
        'files': {
            'enabled': True
        },
        'metadata': {
            'resource_type': None,
            'title': '',
            'creators': [],
            'description': '',
            'rights': [],
            'subjects': [],
            'related_identifiers': [],
            'publisher': 'BIG-MAP Archive'
        }
    }

    metadata_file_path = os.path.join(base_dir_path, metadata_file_path)

    with open(metadata_file_path, 'r') as f:
        partial_metadata = yaml.safe_load(f)

    full_metadata = insert_resource_type(full_metadata, partial_metadata)
    full_metadata['metadata']['title'] = partial_metadata['title']
    full_metadata = insert_creators(full_metadata, partial_metadata)
    full_metadata['metadata']['description'] = partial_metadata['description']
    full_metadata = insert_rights(full_metadata, partial_metadata)
    full_metadata = insert_subjects(full_metadata, partial_metadata)
    full_metadata = insert_related_identifiers(full_metadata, partial_metadata)

    return full_metadata


def insert_resource_type(full_metadata, partial_metadata):
    """
    Inserts a resource type that was extracted from a 'partial' metadata into a 'full' metadata
    Raises an exception if the extracted resource type is different from 'Dataset', 'Software', or 'Other'
    """
    full_metadata['metadata']['resource_type'] = {
        'id': '',
        'title': {
            'en': ''
        }
    }

    if partial_metadata['resource_type'] == 'Dataset':
        full_metadata['metadata']['resource_type']['id'] = 'dataset'
        full_metadata['metadata']['resource_type']['title']['en'] = 'Dataset'
    elif partial_metadata['resource_type'] == 'Software':
        full_metadata['metadata']['resource_type']['id'] = 'software'
        full_metadata['metadata']['resource_type']['title']['en'] = 'Software'
    elif partial_metadata['resource_type'] == 'Other':
        full_metadata['metadata']['resource_type']['id'] = 'other'
        full_metadata['metadata']['resource_type']['title']['en'] = 'Other'
    else:
        raise Exception(f'Invalid resource type {partial_metadata["resource_type"]} in the input metadata file')

    return full_metadata


def insert_creators(full_metadata, partial_metadata):
    """
    Inserts creators (i.e., authors) that were extracted from a 'partial' metadata into a 'full' metadata
    """
    full_metadata['metadata']['creators'] = []
    authors = partial_metadata['authors']

    for author in authors:
        creator = {
            'affiliations': [],
            'person_or_org': {
                'family_name': '',
                'given_name': '',
                'name': '',
                'type': 'personal'
            }
        }

        affiliations = author['affiliations']
        for affiliation in affiliations:
            creator['affiliations'].append({'name': affiliation})

        creator['person_or_org']['family_name'] = author['family_name']
        creator['person_or_org']['given_name'] = author['given_name']
        creator['person_or_org']['name'] = author['family_name'] + ', ' + author['given_name']
        full_metadata['metadata']['creators'].append(creator)

    return full_metadata


def insert_rights(full_metadata, partial_metadata):
    """
    Inserts a right (i.e., a license) that was extracted from a 'partial' metadata into a 'full' metadata. Only the following licenses are accepted:
      - 'BIG-MAP Archive License'
      - 'Creative Commons Attribution Share Alike 4.0 International'
      - 'MIT License'
    """
    full_metadata['metadata']['rights'] = [{
        'description': {
            'en': ''
        },
        'icon': '',
        'id': '',
        'props': {
            'scheme': '',
            'url': ''
        },
        'title': {
            'en': ''
        }
    }]

    if partial_metadata['license'] == 'BIG-MAP Archive License':
        full_metadata['metadata']['rights'][0]['description']['en'] = 'The BIG-MAP Archive License allows re-distribution and re-use of work within the BIG-MAP community.'
        full_metadata['metadata']['rights'][0]['id'] = 'bm-1.0'
        full_metadata['metadata']['rights'][0]['props']['scheme'] = 'spdx'
        full_metadata['metadata']['rights'][0]['props']['url'] = 'https://www.big-map.eu/'
        full_metadata['metadata']['rights'][0]['title']['en'] = 'BIG-MAP Archive License'
    elif partial_metadata['license'] == 'Creative Commons Attribution Share Alike 4.0 International':
        full_metadata['metadata']['rights'][0]['description']['en'] = 'Permits almost any use subject to providing credit and license notice. Frequently used for media assets and educational materials. The most common license for Open Access scientific publications. Not recommended for software.'
        full_metadata['metadata']['rights'][0]['icon'] = 'cc-by-sa-icon'
        full_metadata['metadata']['rights'][0]['id'] = 'cc-by-sa-4.0'
        full_metadata['metadata']['rights'][0]['props']['scheme'] = 'spdx'
        full_metadata['metadata']['rights'][0]['props']['url'] = 'https://creativecommons.org/licenses/by-sa/4.0/legalcode'
        full_metadata['metadata']['rights'][0]['title']['en'] = 'Creative Commons Attribution Share Alike 4.0 International'
    elif partial_metadata['license'] == 'MIT License':
        full_metadata['metadata']['rights'][0]['description']['en'] = 'A short and simple permissive license with conditions only requiring preservation of copyright and license notices. Licensed works, modifications, and larger works may be distributed under different terms and without source code.'
        full_metadata['metadata']['rights'][0]['id'] = 'mit'
        full_metadata['metadata']['rights'][0]['props']['scheme'] = 'spdx'
        full_metadata['metadata']['rights'][0]['props']['url'] = 'https://opensource.org/licenses/MIT'
        full_metadata['metadata']['rights'][0]['title']['en'] = 'MIT License'
    else:
        raise Exception(f'Invalid license {partial_metadata["license"]} in the input metadata file')

    return full_metadata


def insert_subjects(full_metadata, partial_metadata):
    """
    Inserts subjects (i.e., keywords) that were extracted from a 'partial' metadata into a 'full' metadata
    """
    full_metadata['metadata']['subjects'] = [{'subject': keyword} for keyword in partial_metadata['keywords']]

    return full_metadata


def insert_related_identifiers(full_metadata, partial_metadata):
    """
    Inserts related identifiers (i.e., references) that were extracted from a 'partial' metadata into a 'full' metadata. Only the following reference schemes are accepted:
      - 'arxiv'
      - 'doi'
      - 'isbn'
      - 'url'
    """
    full_metadata['metadata']['related_identifiers'] = []
    references = partial_metadata['references']

    for reference in references:
        if reference['scheme'] not in ['arxiv', 'doi', 'isbn', 'url']:
            raise Exception(f'Invalid reference scheme {reference["scheme"]} in the input metadata file')

    for reference in references:
        related_identifier = {
            'identifier': reference['identifier'],
            'relation_type': {
                'id': 'references',
                'title': {'en': 'References'}
            },
            'scheme': reference['scheme']
        }

        full_metadata['metadata']['related_identifiers'].append(related_identifier)

    return full_metadata


def export_to_json_file(base_dir_path, output_file_path, data):
    """
    Exports data to a JSON file
    The file is created if it does not exist or its contents is cleared if it exists
    """
    output_file_path = os.path.join(base_dir_path, output_file_path)

    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)


def change_metadata(record_metadata, base_dir_path, metadata_file_path):
    """
    Updates a record's metadata from a YAML file containing only partial metadata
    """
    metadata_file_path = os.path.join(base_dir_path, metadata_file_path)

    with open(metadata_file_path, 'r') as f:
        partial_metadata = yaml.safe_load(f)

    record_metadata = insert_resource_type(record_metadata, partial_metadata)
    record_metadata['metadata']['title'] = partial_metadata['title']
    record_metadata = insert_creators(record_metadata, partial_metadata)
    record_metadata['metadata']['description'] = partial_metadata['description']
    record_metadata = insert_rights(record_metadata, partial_metadata)
    record_metadata = insert_subjects(record_metadata, partial_metadata)
    record_metadata = insert_related_identifiers(record_metadata, partial_metadata)

    # Update value of 'updated'
    now = datetime.datetime.now(datetime.timezone.utc)
    now_as_string = now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    now_as_string = "{0}:{1}".format(now_as_string[:-2], now_as_string[-2:])
    record_metadata['updated'] = now_as_string

    return record_metadata


def get_name_to_checksum_for_files_in_upload_dir(base_dir_path, upload_dir_path):
    """
    Gets the names and md5 hashes of all files in the upload folder
    """
    upload_dir_path = os.path.join(base_dir_path, upload_dir_path)
    filenames = [
        f for f in os.listdir(upload_dir_path)
        if os.path.isfile(os.path.join(upload_dir_path, f))
    ]

    files_in_upload_dir = []

    for filename in filenames:
        file_path = os.path.join(upload_dir_path, filename)

        with open(file_path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)

        files_in_upload_dir.append(
            {
                'name': filename,
                'checksum': 'md5:' + file_hash.hexdigest()
            })

    return files_in_upload_dir


def get_data_files_in_upload_dir(base_dir_path, upload_dir_path):
    """
    Gets the names of the files in the upload folder
    """
    files = get_name_to_checksum_for_files_in_upload_dir(base_dir_path, upload_dir_path)
    filenames = [f['name'] for f in files]
    return filenames


def get_title_from_metadata_file(base_dir_path, metadata_file_path):
    """
    Extracts the title from a YAML metadata file
    """
    metadata_file_path = os.path.join(base_dir_path, metadata_file_path)

    with open(metadata_file_path, 'r') as f:
        partial_metadata = yaml.safe_load(f)

    title = partial_metadata['title']

    return title


def create_directory(base_dir_path, dir_path):
    """
    Creates a folder if it does not exist
    """
    dir_path = os.path.join(base_dir_path, dir_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def recreate_directory(base_dir_path, dir_path):
    """
    Creates a folder if it does not exist, otherwise recreates it.
    """
    dir_path = os.path.join(base_dir_path, dir_path)

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.makedirs(dir_path)
