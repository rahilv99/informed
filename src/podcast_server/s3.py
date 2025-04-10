import boto3
import os

bucket_name = os.getenv("ASTRA_BUCKET_NAME")
print(f"Astra Bucket name is {bucket_name}")

# Centralized area to define where various stuff is in S3 bucket
def s3LocationMapping(user_id, episode_number, type):
    if (type == "USER_TOPICS"):
        return f"user/{user_id}/user_topics.pkl"
    elif (type == "PULSE"):
        return f"user/{user_id}/pulse.pkl"
    elif (type == "EMAIL"):
        return f"user/{user_id}/{episode_number}/email.pkl"
    elif (type == "PODCAST"):
        return f"user/{user_id}/{episode_number}/podcast.mp3"
    else:
        print(f"Unsupported type {type}")

def save(user_id, episode_number, type, f_path):
    object_key = s3LocationMapping(user_id, episode_number, type)
    # Upload to S3
    try:
        s3 = boto3.client('s3')

        with open(f_path, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, object_key)
        print('Saved data')
    except Exception as e:
        print(f"Error saving to bucket {e}")

def get_s3_url(user_id, episode_number, type):
    object_key = s3LocationMapping(user_id, episode_number, type)
    return f'https://{bucket_name}.s3.us-east-1.amazonaws.com/{object_key}'