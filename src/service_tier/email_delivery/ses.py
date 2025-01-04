import boto3
from botocore.exceptions import ClientError
import os          
from string import Template
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from email_delivery.email_output import EmailOutput
import common.s3

def generate_html(episode_title, email_description, episode):
    # Load the HTML template
    def _load_template(file_path):
        with open(file_path, 'r') as file:
            return Template(file.read())

    # Generate articles list as HTML
    def _generate_articles_html(articles):
        articles_html = ''
        for _, article in articles.iterrows():
            articles_template = _load_template('email_delivery/article.html')
            articles_html += articles_template.substitute(title=article['title'], description=article['description'], url=article['url'])
        return articles_html

    template = _load_template('email_delivery/index.html')
    articles_html = _generate_articles_html(email_description)
    return template.substitute(episode_title=episode_title, episode_number=episode, articles=articles_html)




def send_email(RECIPIENT, SUBJECT, BODY_HTML):
    FILE_PATH = '/tmp/podcast.mp3'

    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = "delivery@auxiomai.com"
    msg['To'] = RECIPIENT

    # Add the HTML body to the email
    msg_body = MIMEMultipart('alternative')
    html_part = MIMEText(BODY_HTML, 'html', 'utf-8')
    msg_body.attach(html_part)
    msg.attach(msg_body)

    # Add the attachment to the email
    with open(FILE_PATH, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{SUBJECT}.mp3"'
        )
        msg.attach(part)

    # Send the email
    client = boto3.client('ses',
                        region_name="us-east-1",
                        aws_access_key_id= os.environ.get('AWS_ACCESS_KEY'), # make sure these are set
                        aws_secret_access_key= os.environ.get('AWS_SECRET_KEY') # make sure these are set
                        )

    try:
        response = client.send_raw_email(
            Source='delivery@auxiomai.com',
            Destinations=[RECIPIENT],
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
    user_id = payload.get("user_id")
    user_email = payload.get("user_email")
    episode = payload.get("episode")
    ep_type = payload.get("ep_type")

    headers = EmailOutput(user_id)
    email_description = headers.email_description
    episode_title = headers.episode_title

    common.s3.restore(user_id, "PODCAST", "/tmp/podcast.mp3")

    html = generate_html(episode_title, email_description, episode)

    send_email(user_email, episode_title, html)

if __name__ == "__main__":
    handler(None)