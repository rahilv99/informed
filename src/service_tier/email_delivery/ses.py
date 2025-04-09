import boto3
import os          
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2 
import json
from datetime import datetime
from email_delivery.email_output import EmailOutput
import common.s3

db_access_url = os.environ.get('DB_ACCESS_URL')

def update_db(user_id, episode_title, topics, episode_number, episode_type, mp3_file_url):
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO podcasts (title, user_id, articles, episode_number, episode_type, audio_file_url, date, completed)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s)
            RETURNING id
        """, (episode_title, user_id, json.dumps(topics), episode_number, episode_type, mp3_file_url, datetime.now(), False))
        

        # Update user's episode count and podcast status
        cursor.execute("""
            UPDATE users 
            SET episode = episode + 1,
                delivered = %s
            WHERE id = %s
        """, (datetime.now(), user_id))

        conn.commit()
        print(f"Successfully updated podcast and user tables for user {user_id}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def generate_html(episode_title, topics, episode, name):
    # Load the HTML template
    def _load_template(file_path):
        with open(file_path, 'r') as file:
            return Template(file.read())

    # Generate articles list as HTML
    def _generate_articles_html(topics):
        articles_html = ''
        for topic in topics:
            articles_template = _load_template('email_delivery/article.html')
            articles_html += articles_template.substitute(title=topic['title'], description=topic['description'], url=topic['gov'][0][1])
        return articles_html

    template = _load_template('email_delivery/index.html')
    articles_html = _generate_articles_html(topics)
    return template.substitute(episode_title=episode_title, episode_number=episode, articles=articles_html)


def send_email(RECIPIENT, SUBJECT, BODY_HTML):

    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = "Auxiom <Auxiom@auxiomai.com>"
    msg['To'] = RECIPIENT

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
            Source='delivery@auxiomai.com',
            Destinations=[RECIPIENT, 'rahilv99@gmail.com'],
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
    name = payload.get("user_name")
    episode = payload.get("episode")
    ep_type = payload.get("ep_type")

    headers = EmailOutput(user_id, episode)
    topics = headers.topics
    episode_title = headers.episode_title

    if len(name.split()) > 1:
        name = name.split()[0]

    common.s3.restore(user_id, episode,"PODCAST", "/tmp/podcast.mp3")

    html = generate_html(episode_title, topics, episode, name)

    send_email(user_email, episode_title, html)

    s3_url = common.s3.get_s3_url(user_id, episode, "PODCAST")
    # Update podcast and user tables 
    update_db(user_id, episode_title, topics, episode, ep_type, s3_url)

if __name__ == "__main__":
    handler(None)