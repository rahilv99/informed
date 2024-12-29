import boto3
from botocore.exceptions import ClientError
import os

SENDER = "product@auxiomai.com"
RECIPIENT = "rahilv99@gmail.com"

SUBJECT = "Amazon SES Test "     

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

CHARSET = "UTF-8"

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
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                }
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER
    )

except ClientError as e:
    print(e.response['Error']['Message'])
else:
    print("Email sent! Message ID:"),
    print(response['MessageId'])