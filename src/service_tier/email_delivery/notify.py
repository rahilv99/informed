import boto3
import os          
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from string import Template


db_access_url = 'postgresql://auxiompostgres:astrapodcast!@auxiom-db.cvoqq0ms6fsc.us-east-1.rds.amazonaws.com:5432/postgres' #os.environ.get('DB_ACCESS_URL')
print(db_access_url)

def generate_html(name, keywords):
    # Load the HTML template
    def _load_template(file_path):
        with open(file_path, 'r') as file:
            return Template(file.read())

    template = _load_template('email_delivery/notify.html')
    return template.substitute(user=name, keywords=keywords)

def send_email(RECIPIENT, BODY_HTML):

    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'Your Axuiom podcast'
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
    keywords = payload.get("keywords")


    if len(name.split()) > 1:
        name = name.split()[0]

    # format keywords
    formatted = ', '.join(keywords[:-1])
    formatted += f' and {keywords[-1]}'

    html = generate_html(name, formatted)

    send_email(user_email, html)

if __name__ == "__main__":
    user_id = '27'
    user_email = 'rahilv99@gmail.com'
    name = 'Rahil Verma'
    keywords = ['python', 'aws', 'devops']
    
    if len(name.split()) > 1:
        name = name.split()[0]

    # format keywords
    formatted = ', '.join(keywords[:-1])
    formatted += f' and {keywords[-1]}'

    html = generate_html(name, formatted)

    send_email(user_email, html)