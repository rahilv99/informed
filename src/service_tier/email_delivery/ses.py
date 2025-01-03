import boto3
from botocore.exceptions import ClientError
import os          
from string import Template


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
            articles_template = _load_template('article.html')
            articles_html += articles_template.substitute(title=article['title'], description=article['description'], url=article['url'])
        return articles_html

    template = _load_template('index.html')
    articles_html = _generate_articles_html(email_description)
    template.substitute(episode_title=episode_title, episode_number=episode, articles=articles_html)



def send_email(RECIPIENT, SUBJECT, BODY_HTML):
    attachment = '/tmp/podcast.mp3'

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
            Source='delivery@auxiomai.com'
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
    ep_type = payload.get("ep_type")

    headers = EmailOutput(user_id)
    email_description = headers.email_description
    episode_title = headers.episode_title

    common.s3.restore(user_id, "PODCAST", "/tmp/podcast.mp3")

    html = generate_html(episode_title, email_description, episode)

    send_email(user_email, episode_title, html)

if __name__ == "__main__":
    handler(None)