import boto3
import os


def handler(payload):
    bucket_name = os.getenv("BUCKET_NAME")
    prefix = payload.get('prefix', 'gnews/')
    
    s3 = boto3.client('s3')

    # List all objects in the folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Delete all objects
    if 'Contents' in response:
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        
        delete_response = s3.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects_to_delete}
        )
        
        print(f"Deleted {len(delete_response.get('Deleted', []))} objects.")
    else:
        print("No files found in the folder.")
