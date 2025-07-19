import boto3
import os          
import psycopg2
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai

db_access_url = os.environ.get('DB_ACCESS_URL')

GOOGLE_API_KEY= os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

summary_model = genai.GenerativeModel('gemini-2.0-flash') # $0.075 /M input  $0.30 /M output tokens 


def episode_title(article_titles):
    prompt = "Create a newsletter episode title based on the title of the articles discussed. Only include the generated title itself; avoid any introductions, explanations, or meta-comments. Titles: " + ", ".join(article_titles)
    
    response = summary_model.generate_content(prompt,
                                                generation_config = genai.GenerationConfig(
                                            max_output_tokens=50))
    return ' '.join(response.text.strip().split())


def get_articles_by_ids(article_ids):
    """
    Retrieve articles from the database using their IDs
    Returns a list of dictionaries with id, title, and summary
    """
    if not article_ids:
        return []
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        
        cursor = conn.cursor()
        
        # Create placeholders for the IN clause
        placeholders = ','.join(['%s'] * len(article_ids))
        query = f"""
            SELECT id, title, summary 
            FROM articles 
            WHERE id IN ({placeholders})
        """
        
        cursor.execute(query, article_ids)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        articles = []
        for row in results:
            articles.append({
                'id': row[0],
                'title': row[1],
                'summary': row[2]
            })
        
        cursor.close()
        conn.close()
        
        return articles
        
    except Exception as e:
        print(f"Error retrieving articles from database: {e}")
        return []


def generate_html(episode_title, articles, episode, name):
    # Load the HTML template
    def _load_template(file_path):
        with open(file_path, 'r') as file:
            return Template(file.read())

    # Generate articles list as HTML
    def _generate_articles_html(articles):
        articles_html = ''
        for article in articles:
            articles_template = _load_template('logic/templates/article.html')
            url = f"https://auxiomai.com/articles/{article['id']}"
            articles_html += articles_template.substitute(
                title=article['title'], 
                description=article['summary'], 
                url=url
            )
        return articles_html

    template = _load_template('logic/templates/index.html')
    articles_html = _generate_articles_html(articles)
    return template.substitute(episode_title=episode_title, episode_number=episode, articles=articles_html, user=name)


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
    recommendations = payload.get("recommendations", [])

    # Get articles from database using the recommendation IDs
    articles = get_articles_by_ids(recommendations)

    if len(name.split()) > 1:
        name = name.split()[0]

    ep_title = episode_title([article['title'] for article in articles])

    html = generate_html(ep_title, articles, episode, name)

    send_email(user_email, ep_title, html)


if __name__ == "__main__":
    # Test payload with article recommendations
    test_payload = {
        'user_id': '27',
        'user_email': 'rahilv99@gmail.com',
        'user_name': 'Rahil Verma',
        'episode': '10',
        'recommendations': [3899, 3900, 3901]  # List of article IDs to retrieve from database
    }
    
    handler(test_payload)
