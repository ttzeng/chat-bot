# Import Google Cloud client library
# Reference: https://cloud.google.com/python/docs/reference/storage
from google.cloud import storage
from google.api_core.exceptions import NotFound

def cloud_storage_upload_object (bucket_name: str, blob_name: str,
                                 data: any, content_type: str = 'application/octet-stream'):
    # Instantiates a client for interacting with the Google Cloud Storage API
    client = storage.Client()
    try:
        # Retrieve the bucket
        bucket = client.get_bucket(bucket_name)
        # Constructs a blob object in the bucket
        blob = bucket.blob(blob_name)
        # Upload contents of this blob
        blob.upload_from_string(data, content_type=content_type)
    except NotFound:
        print("Bucket '{}' not found".format(bucket_name))

def cloud_storage_download_object (bucket_name: str, blob_name: str) -> bytes:
    # Instantiates a client for interacting with the Google Cloud Storage API
    client = storage.Client()
    try:
        # Retrieve the bucket
        bucket = client.get_bucket(bucket_name)
        # Get a blob object by name
        blob = bucket.get_blob(blob_name)
        # Download the contents of this blob as a bytes object
        if blob is not None:
            return blob.download_as_bytes()
    except NotFound:
        print("Bucket '{}' not found".format(bucket_name))
    return None
