import boto3
from botocore.exceptions import ClientError
import os          
from string import Template
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2 
import json

db_access_url = "postgresql://auxiompostgres:astrapodcast!@auxiom-db.cvoqq0ms6fsc.us-east-1.rds.amazonaws.com:5432/postgres"

def get_emails():
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users")
        emails = cursor.fetchall()
        return emails
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def send_email(RECIPIENTS):
    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'Big things are coming...'
    msg['From'] = "newsletter@auxiomai.com"
    msg['To'] = RECIPIENTS

    # Add the HTML body to the email
    msg_body = MIMEMultipart('alternative')
    html_part = MIMEText(BODY_HTML, 'html', 'utf-8')
    msg_body.attach(html_part)
    msg.attach(msg_body)

    # Send the email
    client = boto3.client('ses',
        region_name="us-east-1",
        aws_access_key_id= os.environ.get('AWS_ACCESS_KEY'), # make sure these are set
        aws_secret_access_key= os.environ.get('AWS_SECRET_KEY') # make sure these are set
        )

    try:
        response = client.send_raw_email(
            Source='newsletter@auxiomai.com',
            Destinations=RECIPIENTS,
            RawMessage={
                'Data': msg.as_string(),
            }
        )
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    except client.exceptions.MessageRejected as e:
        print(f"Email rejected: {e}")
    except client.exceptions.ClientError as e:
        print(f"Unexpected error: {e}")


# Main Execution
def handler(payload):
    emails = get_emails()

    send_email(emails)

if __name__ == "__main__":
    handler(None)