import boto3
import os          
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2 
from jinja2 import Template
import re
from bs4 import BeautifulSoup



def get_users_with_embeddings():
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        cursor.execute("SELECT email, embedding FROM users")
        users = cursor.fetchall()
        return users
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_recommended_article(user_embedding, limit=1):
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, content, embedding <=> %s::vector AS distance
            FROM articles
            ORDER BY distance
            LIMIT %s
        """, (user_embedding, limit))
        
        result = cursor.fetchone()
        return result
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def process_paragraphs(content):
    """Process HTML content with <p> tags and generate paragraph instances"""
    # Load the paragraph template
    with open('paragraph.html', 'r') as file:
        paragraph_template_content = file.read()
    
    paragraph_template = Template(paragraph_template_content)
    
    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all <p> tags
    p_tags = soup.find_all('p')
    
    # Generate paragraph instances
    paragraph_instances = []
    for p_tag in p_tags:
        # Get the text content of the paragraph
        paragraph_content = p_tag.get_text().strip()
        if paragraph_content:  # Only process non-empty paragraphs
            # Render the paragraph template with the content
            rendered_paragraph = paragraph_template.render(content=paragraph_content)
            paragraph_instances.append(rendered_paragraph)
    
    # Concatenate all paragraph instances
    concatenated_paragraphs = ''.join(paragraph_instances)
    
    return concatenated_paragraphs

def generate_html(title, content):
    """Generate HTML content using the template"""
    with open('index.html', 'r') as file:
        template_content = file.read()
    
    template = Template(template_content)
    
    # Process the content to extract and format paragraphs
    processed_paragraphs = process_paragraphs(content)

    rendered = template.render(title=title, paragraphs=processed_paragraphs)

    return rendered

def send_email(recipient_email, title, content):
    # Generate HTML content with the recommended article
    BODY_HTML = generate_html(title, content)

    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'check this out'
    msg['From'] = "Auxiom <newsletter@auxiomai.com>"
    msg['To'] = recipient_email

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
            Destinations=[recipient_email],
            RawMessage={
                'Data': msg.as_string(),
            }
        )
        print(f"Email sent to {recipient_email}! Message ID: {response['MessageId']}")

    except client.exceptions.MessageRejected as e:
        print(f"Email rejected for {recipient_email}: {e}")
    except client.exceptions.ClientError as e:
        print(f"Unexpected error for {recipient_email}: {e}")


# Main Execution
def handler(payload):
    # Get users with their embeddings
    users = get_users_with_embeddings()
    
    # If no users found, use test data
    if not users:
        print("No users found in database, using test data")
        users = [('rahilv99@gmail.com', None)]
    
    for email, embedding in users:
        if embedding:
            # Get recommended article based on user's embedding
            recommended = get_recommended_article(embedding)
            
            if recommended:
                title, content, distance = recommended
                print(f"Sending personalized newsletter to {email} with article: {title}")
                send_email(email, title, content)
            else:
                print(f"No recommendations found for {email}")
        else:
            # For users without embedding, use a default article
            print(f"No embedding found for {email}, using default content")
            default_title = "Welcome to Your Personalized Newsletter"
            default_content = "We're working on personalizing your content. Stay tuned for more relevant articles!"
            send_email(email, default_title, default_content)

if __name__ == "__main__":
    handler(None)
