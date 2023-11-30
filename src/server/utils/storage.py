from google.cloud import storage


class CloudStorage:
    def __init__(self, project_name, bucket_name):
        self.project_name = project_name
        self.bucket_name = bucket_name
        self.storage_client = storage.Client(project_name)
        self.bucket = self.storage_client.bucket(bucket_name)

    def upload_blob(self, source_file_name, destination_blob_name):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)

    def download_blob(self, source_blob_name, destination_file_name):
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def check_blob_exist(self, blob_name):
        blob = self.bucket.blob(blob_name)
        return blob.exists()
