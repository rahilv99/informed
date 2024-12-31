import boto3
import pickle
import os

bucket_name = os.getenv("ASTRA_BUCKET_NAME")
print(f"Astra Bucket name is {bucket_name}")

# Centralized area to define where various stuff is in S3 bucket
def s3LocationMapping(user_id, type):
    if (type == "USER_TOPICS"):
        return f"user/{user_id}/user_topics.pkl"
    elif (type == "PULSE"):
        return f"user/{user_id}/pulse.pkl"
    elif (type == "EMAIL"):
        return f"user/{user_id}/email.pkl"
    elif (type == "PODCAST"):
        return f"user/{user_id}/podcast.mp3"
    else:
        print(f"Unsupported type {type}")

def save_serialized(user_id, type, data):
    object_key = s3LocationMapping(user_id, type)
    # Serialize the data
    serialized_data = pickle.dumps(data)

    # Upload to S3
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=serialized_data)
        print('Saved serialized data')
    except Exception as e:
        print(f"Error saving to bucket {e}")

def restore_serialized(user_id, type):
    object_key = s3LocationMapping(user_id, type)
    # Download serialized data from S3
    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        serialized_data = response['Body'].read()
        print('Retrieved serialized data')
    except Exception as e:
        print(f"Error reading from bucket {e}")
        return {}

    # Deserialize the data
    data = pickle.loads(serialized_data)
    return data

def save(user_id, type, f_path):
    object_key = s3LocationMapping(user_id, type)
    # Upload to S3
    try:
        s3 = boto3.client('s3')
        s3.upload_fileobj(f_path, bucket_name, object_key)
        print('Saved data')
    except Exception as e:
        print(f"Error saving to bucket {e}")

def restore(user_id, type, f_path):
    object_key = s3LocationMapping(user_id, type)
    # Download data from S3
    s3 = boto3.client('s3')

    try:
        s3.download_fileobj(bucket_name, object_key, f_path)
        print('Retrieved data')
    except Exception as e:
        print(f"Error reading from bucket {e}")
        return {}
    

def restore_from_system(type, f_path):

    def _s3LocationMapping(type):
        if type == "INTRO":
            return f"system/intro_music.mp3"
    
    # Download data from S3
    s3 = boto3.client('s3')

    try:
        object_key = _s3LocationMapping(type)
        s3.download_fileobj(bucket_name,object_key, f_path)
        print('Retrieved data')
    except Exception as e:
        print(f"Error reading from bucket {e}")
        return {}