from azure.storage.blob import BlobServiceClient
import uuid

def upload_image(file, connection_string, container_name):

    blob_service = BlobServiceClient.from_connection_string(connection_string)

    blob_name = str(uuid.uuid4()) + "_" + file.filename

    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    blob_client.upload_blob(file, overwrite=True)

    url = f"https://{blob_service.account_name}.blob.core.windows.net/{container_name}/{blob_name}"

    return url