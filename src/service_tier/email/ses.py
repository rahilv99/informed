import boto3
from botocore.exceptions import ClientError
import os          

from email_output import EmailOutput
import common.s3

def send_email(RECIPIENT, SUBJECT, email_description, episode):

    # Substitute with HTML populated with user data
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Amazon SES Test (SDK for Python)</h1>
    <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
        AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """  
    
    attachment = 'tmp/podcast.mp3'

    client = boto3.client('ses',
                        region_name="us-east-1",
                        aws_access_key_id= os.environ.get('AWS_ACCESS_KEY'), # make sure these are set
                        aws_secret_access_key= os.environ.get('AWS_SECRET_KEY') # make sure these are set
                        )

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [RECIPIENT],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': BODY_HTML,
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': SUBJECT,
                },
            },
            Source='product@auxiomai.com'
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


# Main Execution
def handler(payload):
    user_id = payload.get("user_id")
    user_email = payload.get("user_email")
    episode = payload.get("episode")
    type = payload.get("type")

    headers = EmailOutput(user_id)
    email_description = headers.email_description
    episode_title = headers.episode_title

    common.s3.restore(user_id, "PODCAST", "tmp/podcast.mp3")

    send_email(user_email, episode_title, email_description, episode)

if __name__ == "__main__":
    handler(None)