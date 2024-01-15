import json
import os
from datetime import date


from big_map_archive_api_client.client.rest_api_connection import \
    RestAPIConnection
from big_map_archive_api_client.utils import (
    change_metadata, generate_full_metadata,
    get_name_to_checksum_for_files_in_upload_dir)


class ArchiveAPIClientError(Exception):
    """ArchiveAPIClient exceptions"""
    pass


class ArchiveAPIClient:
    """
    Class to interact with BMA's API
    """

    def __init__(self, domain_name, port, token):
        """
        Initialize internal variables
        """
        self._connection = RestAPIConnection(domain_name, port)
        self._token = token

    def post_records(self, base_dir_path, metadata_file_path):
        """
        Creates a draft on the archive from provided metadata
        Raises an HTTPError exception if the request fails
        Returns the newly created draft's id
        """
        resource_path = '/api/records'
        metadata = generate_full_metadata(base_dir_path, metadata_file_path)
        payload = json.dumps(metadata)
        response = self._connection.post(resource_path, self._token, payload)
        response.raise_for_status()
        return response.json()

    def post_files(self, record_id, filenames):
        """
        Updates a record's metadata by specifying the files that should be linked to it
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/files'

        # Create the payload specifying the files to be attached to the record
        key_to_filename = []
        for filename in filenames:
            key_to_filename.append({'key': filename})

        payload = json.dumps(key_to_filename)
        response = self._connection.post(resource_path, self._token, payload)
        response.raise_for_status()
        return response.json()

    def put_content(self, record_id, base_dir_path, upload_dir_path, filename):
        """
        Uploads a file's content
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/files/{filename}/content'
        file_path = os.path.join(base_dir_path, upload_dir_path, filename)

        with open(file_path, 'rb') as f:
            payload = f
            response = self._connection.put(resource_path, self._token, payload, 'application/octet-stream')

        response.raise_for_status()
        return response.json()

    def post_commit(self, record_id, filename):
        """
        Completes the upload of a file's content
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/files/{filename}/commit'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def get_draft(self, record_id):
        """
        Gets a draft's metadata
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def put_draft(self, record_id, metadata):
        """
        Updates a draft's metadata
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft'
        payload = json.dumps(metadata)
        response = self._connection.put(resource_path, self._token, payload)
        response.raise_for_status()
        return response.json()

    def get_community_id(self, slug):
        """
        Get community id
        Raises an HTTPError exception if the request fails
        @param slug: slug of the community
        @returns: community uuid for given slug
        """
        resource_path = f'/api/communities?q=slug:{slug}'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        result = response.json()
        try:
            assert result["hits"]["total"] == 1
        except Exception:
            raise ArchiveAPIClientError(f"There is no community or more than one community for slug '{slug}'")

        return result["hits"]["hits"][0]["id"]

    def put_draft_community(self, record_id, community_id):
        """
        Attribute draft to community - create a review in parent
        Raises an HTTPError exception if the request fails
        @param record_id: record id
        @param community_id: community uuid
        @returns: json of review
        """
        review = {
            "receiver": {
                "community": community_id
            },
            "type": "community-submission"
        }
        resource_path = f'/api/records/{record_id}/draft/review'
        payload = json.dumps(review)
        response = self._connection.put(resource_path, self._token, payload)
        response.raise_for_status()
        return response.json()

    def post_review(self, record_id):
        """
        Submit review to community - create a request to include a record in the community
        (that is equivalent to publish the record if the review policy is open)
        Raises an HTTPError exception if the request fails
        @param record_id: record id
        @returns: json of request
        """
        resource_path = f'/api/records/{record_id}/draft/actions/submit-review'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def delete_draft(self, record_id):
        """
        Deletes a draft
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft'
        response = self._connection.delete(resource_path, self._token)
        response.raise_for_status()

    def insert_publication_date(self, record_id):
        """
        Inserts a publication date into a record's metadata
        """
        response = self.get_draft(record_id)
        response['metadata']['publication_date'] = date.today().strftime('%Y-%m-%d')  # e.g., '2020-06-01'
        response = self.put_draft(record_id, response)

    def post_publish(self, record_id):
        """
        Publishes a draft to the archive (i.e., shares a record with all archive users)
        Raises an HTTPError exception if the request fails
        Note: starting from invenioRDM v12 this api call is replaced by post_review
        """
        resource_path = f'/api/records/{record_id}/draft/actions/publish'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def get_record(self, record_id):
        """
        Gets a published record's metadata
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def get_records(self, all_versions, response_size):
        """
        Gets published records' metadata
        Raises an HTTPError exception if the request fails
        """
        response_size = int(float(response_size))
        resource_path = f'/api/records?allversions={all_versions}&size={response_size}'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def post_draft(self, record_id):
        """
        Creates a draft from a published record: same version with same record id
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def post_versions(self, record_id):
        """
        Creates a draft from a published record: a new version with a different record id
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/versions'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def get_files(self, record_id):
        """
        Gets a draft's linked files (with their names and their md5 hashes)
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/files'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def delete_filename(self, record_id, filename):
        """
        Removes a link to a file from a draft
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/files/{filename}'
        response = self._connection.delete(resource_path, self._token)
        response.raise_for_status()

    def post_file_import(self, record_id):
        """
        Imports all file links from a published record into a draft (new version)
        This avoids re-uploading files, which would cause duplication on the data store
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/records/{record_id}/draft/actions/files-import'
        response = self._connection.post(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def update_metadata(self, record_id, base_dir_path, metadata_file_path):
        """
        Updates the metadata of a draft using a file's content
        """
        record_metadata = self.get_draft(record_id)
        record_metadata = change_metadata(record_metadata, base_dir_path, metadata_file_path)
        self.put_draft(record_id, record_metadata)

    def upload_files(self, record_id, base_dir_path, upload_dir_path, filenames):
        """
        Uploads files located in the input folder to BIG-MAP Archive and
        insert file links into a draft
        """
        self.post_files(record_id, filenames)

        for filename in filenames:
            self.put_content(record_id, base_dir_path, upload_dir_path, filename)
            self.post_commit(record_id, filename)

    def get_name_to_checksum_for_linked_files(self, record_id):
        """
        Gets the names and md5 hashes of a draft's linked files
        """
        response = self.get_files(record_id)
        entries = response['entries']

        linked_files = [
            {
                'name': entry['key'],
                'checksum': entry['checksum']
            } for entry in entries]

        return linked_files

    def get_links(self, record_id):
        """
        Gets the names of a draft's linked files
        """
        linked_files = self.get_name_to_checksum_for_linked_files(record_id)
        filenames = [file['name'] for file in linked_files]
        return filenames

    def delete_links(self, record_id, filenames):
        """
        Deletes file links from a draft
        """
        for filename in filenames:
            self.delete_filename(record_id, filename)

    def get_missing_files(self, record_id, base_dir_path, upload_dir_path):
        """
         Gets all linked files of a draft that are not in the input folder
        """
        linked_files = self.get_name_to_checksum_for_linked_files(record_id)
        files_in_upload_dir = get_name_to_checksum_for_files_in_upload_dir(base_dir_path, upload_dir_path)
        filenames = [f['name'] for f in linked_files if f not in files_in_upload_dir]

        return filenames

    def get_changed_content_files(self, record_id, base_dir_path, upload_dir_path):
        """
        Gets all linked files of a draft for which there is a file in the input folder with the same name but a different content
        """
        linked_files = self.get_name_to_checksum_for_linked_files(record_id)
        files_in_upload_dir = get_name_to_checksum_for_files_in_upload_dir(base_dir_path, upload_dir_path)

        filenames = []

        # Iterate over the linked files
        for file in linked_files:
            name = file['name']
            checksum = file['checksum']

            # How many files in the upload directory with the same name but a different content are there?
            same_name_different_content_files = [f for f in files_in_upload_dir
                                                 if (f['name'] == name and f['checksum'] != checksum)]

            if len(same_name_different_content_files) == 1:
                filenames.append(name)

        return filenames

    def get_links_to_delete(self, record_id, base_dir_path, upload_dir_path, link_all_files_from_previous):
        """
        Reasons for deleting a file link in a draft:
          - the linked file is not in the input folder and 'discard' is set to 'True'
          - a file with the same name as the linked file appears in the input folder but its content is different (i.e., different md5 hashes)
        """
        filenames = self.get_changed_content_files(record_id, base_dir_path, upload_dir_path)

        if not link_all_files_from_previous:
            filenames += self.get_missing_files(record_id, base_dir_path, upload_dir_path)

        # Remove duplicates
        filenames = list(set(filenames))

        return filenames

    def get_files_to_upload(self, record_id, base_dir_path, upload_dir_path):
        """
        Get all data files in the upload directory for which there is currently no link
        """
        input_folder_files = get_name_to_checksum_for_files_in_upload_dir(base_dir_path, upload_dir_path)
        linked_files = self.get_name_to_checksum_for_linked_files(record_id)
        filenames = [f['name'] for f in input_folder_files if f not in linked_files]

        return filenames

    def get_user_records(self, all_versions, response_size):
        """
        Gets the metadata for all records (including drafts) of a user
        Raises an HTTPError exception if the request fails
        """
        resource_path = f'/api/user/records?allversions={all_versions}&size={response_size}'
        response = self._connection.get(resource_path, self._token)
        response.raise_for_status()
        return response.json()

    def get_latest_versions(self):
        """
        Gets the ids and the statuses of the latest version of all entries belonging to a user
        """
        all_versions = False
        response_size = int(float('1e6'))
        response = self.get_user_records(all_versions, response_size)
        latest_versions = response['hits']['hits']
        latest_versions = [{'id': v['id'], 'is_published': v['is_published']} for v in latest_versions]
        return latest_versions

    def get_published_user_records_with_given_title(self, title):
        """
        Gets the ids of the records owned by the user that are published and have a given title
        """
        all_versions = True
        response_size = int(float('1e6'))
        response = self.get_user_records(all_versions, response_size)
        user_records = response['hits']['hits']
        record_ids = [r['id'] for r in user_records if (r['is_published'] and r['metadata']['title'] == title)]

        return record_ids

    def exists_and_is_published(self, record_id):
        """
        Returns True if the record id corresponds to a published record on the BIG-MAP Archive that is owned by the user, False otherwise
        """
        # Gets the ids of the records owned by the user that are published
        all_versions = True
        response_size = int(float('1e6'))
        response = self.get_user_records(all_versions, response_size)
        user_records = response['hits']['hits']
        record_ids = [r['id'] for r in user_records if r['is_published']]

        return True if record_id in record_ids else False

    def get_record_title(self, record_id):
        """
        Returns the title of a published record
        """
        response = self.get_record(record_id)
        title = response['metadata']['title']

        return title
