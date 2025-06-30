import re
import google.generativeai as genai
import os
import psycopg2 
import json
from datetime import datetime

import common.s3

db_access_url = os.environ.get('DB_ACCESS_URL')

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

summary_model = genai.GenerativeModel('gemini-1.5-flash')  # $0.075 /M input  $0.30 /M output tokens 
article_model = genai.GenerativeModel('gemini-2.0-flash')  # $0.10 /M input $0.40 /M output tokens


### Underwriter - Researches documents in a cluster
def underwriter_research(cluster_df):
    """
    Research component that analyzes documents in a cluster and creates detailed notes
    for the article writer.
    
    Args:
        cluster_df: DataFrame containing documents in a cluster with columns:
                   'source', 'type', 'title', 'text', 'url', 'keyword', 'publisher'
    
    Returns:
        Dictionary with research notes for each document type
    """
    research_notes = {
        'primary_doc': {},
        'secondary_docs': [],
        'news_articles': []
    }
    
    # Process primary government document
    primary_doc = cluster_df[cluster_df['type'] == 'primary'].iloc[0]
    primary_prompt = f"""
    You are a research analyst preparing notes for an article about government documents and their impact on current events.
    
    Analyze this primary government document and create detailed research notes that will help an article writer.
    
    DOCUMENT:
    Title: {primary_doc['title']}
    Text: {primary_doc['text'][1000:50000]}
    
    Create research notes with the following sections:
    1. Key Points: Main ideas and decisions in the document
    2. Important Figures: Key people, organizations, or entities mentioned
    3. Metrics & Deadlines: Any specific numbers, amounts, or timeframes
    4. Implications: Potential impact or consequences of this document
    5. Context: Historical or policy context that would help readers understand
    
    Format your response as a structured set of notes, not as a narrative.
    Keep your response less than 300 tokens.
    """
    
    primary_response = summary_model.generate_content(
        primary_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=400,
            temperature=0.2
        )
    )
    
    research_notes['primary_doc'] = {
        'title': primary_doc['title'],
        'url': primary_doc['url'],
        'notes': primary_response.text
    }
    
    # Process secondary government documents
    secondary_docs = cluster_df[cluster_df['type'] == 'secondary']
    for _, doc in secondary_docs.iterrows():
        secondary_prompt = f"""
        You are a research analyst preparing notes for an article about government documents and their impact on current events.
        
        Analyze this government document and create research notes that will help an article writer.
        
        DOCUMENT:
        Title: {doc['title']}
        Text: {doc['text'][1000:50000]}
        
        Create research notes with the following sections:
        1. Key Points: Main ideas and decisions in the document
        2. Important Figures: Key people, organizations, or entities mentioned
        3. Metrics & Deadlines: Any specific numbers, amounts, or timeframes
        4. Implications: Potential impact or consequences of this document
        5. Context: Historical or policy context that would help readers understand

        Format your response as a structured set of notes, not as a narrative.
        Keep your response less than 200 tokens.
        """
        
        secondary_response = summary_model.generate_content(
            secondary_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=200,
                temperature=0.2
            )
        )
        
        research_notes['secondary_docs'].append({
            'title': doc['title'],
            'url': doc['url'],
            'notes': secondary_response.text
        })
    
    # Process news articles
    news_articles = cluster_df[cluster_df['type'] == 'news']
    for _, article in news_articles.iterrows():
        research_notes['news_articles'].append({
            'title': article['title'],
            'publisher': article['publisher'],
            'url': article['url'],
            'notes': ''  # Keeping empty for now as in nlp.py, can be filled with news response text if needed
        })
    
    return research_notes


### Article Writer - Creates an article for a cluster based on underwriter's research
def create_cluster_article(research_notes):
    """
    Creates an article for an entire cluster based on the underwriter's research.
    
    Args:
        research_notes: Dictionary with research notes from the underwriter
    
    Returns:
        Dictionary containing the article title and content
    """

    tokens = 500 # less than 500 words  

    # Extract information from research notes
    primary_doc = research_notes['primary_doc']
    secondary_docs = research_notes['secondary_docs']
    news_articles = research_notes['news_articles']
    
    # Create a prompt for the article writer
    system_prompt = f"""
    You are a professional writer for "Auxiom," a publication that breaks down complex government documents and their impact on current events.
    
    Your task is to write a concise, informative, and engaging article based on government documents and news coverage.
    You have been provided with research notes from a research analyst, which you will use to generate content.

    Output exactly:
    "Title": <Descriptive, attention-grabbing title of the article>,
    "People": <List of specific full names of the top (at most) 3 people related to the documents>
    "Keywords": <List the top (at most) 5 keywords related to the article>,
    "Article": <Content of the article in paragraph format without meta-comments or introductions>
    
    **WRITING GUIDELINES:**
    * Write in a clear, professional, yet engaging tone
    * Use active voice and vivid language
    * Include specific details, numbers, and quotes when relevant
    * Connect government actions (primary + secondary articles) to real-world impacts (news articles)
    * Be charismatic and engaging while maintaining credibility
    
    **ARTICLE STRUCTURE:**
    1. Start with a compelling hook that highlights why this matters
    2. Explain the primary government document and its key provisions
    3. Connect related government documents to show the bigger picture
    4. Discuss how current news reflects or responds to these government actions
    5. End with implications and what readers should watch for next
    
    **STYLE TIPS:**
    * Use short paragraphs for readability
    * Include transitions between ideas
    * Avoid jargon; explain technical terms when necessary
    * Write as if explaining to an intelligent friend
    * Be informative but not dry; engaging but not sensational
    
    Remember: This article must be approximately {tokens} tokens long.
    
    **RESEARCH NOTES:**
    
    PRIMARY DOCUMENT:
    Title: {primary_doc['title']}
    {primary_doc['notes']}
    
    SECONDARY DOCUMENTS:
    """
    
    # Add secondary documents
    for i, doc in enumerate(secondary_docs):
        system_prompt += f"""
        Document {i+1}:
        Title: {doc['title']}
        {doc['notes']}
        """
    
    # Add news articles
    system_prompt += """
    NEWS ARTICLES:
    """
    
    for i, article in enumerate(news_articles):
        system_prompt += f"""
        Article {i+1}:
        Title: {article['title']}
        Publisher: {article['publisher']}
        {article['notes']}
        """

    
    # Define your desired JSON schema
    json_schema = {
        "type": "object",
        "properties": {
            "Title": {
                "type": "string"
            },
            "People": {
                "type": "list",
                "items": {
                    "type": "string"
                }
            },
            "Keywords": {
                "type": "list",
                "items": {
                    "type": "string"
                }
            },
            "Article": {
                "type": "string"
            }
        },
        "required": ["Title", "People", "Article"],
    }

    # Generate the article
    response = article_model.generate_content(
        system_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=tokens*2,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=json_schema
        )
    )
    
    # Parse the response as JSON
    article_json = json.loads(response.text)
    title = article_json.get("Title", "Auxiom Article").strip()
    content = article_json.get("Article", "").strip()
    people = article_json.get("People", "").strip()
    keywords = article_json.get("Keywords", [])

    time = round(len(content.split()) / 225)  # Average reading speed is 225 words per minute, rounded to 2 decimals

    return {
        'title': title,
        'content': content,
        'people': people,
        'tags': keywords,
        'research_notes': research_notes,
        'time': time
    }


def generate_summary(article_title, article_content, research_notes):
    """
    Generates a newsletter blurb about the article for email delivery.
    
    Args:
        article_title: Title of the article
        article_content: Content of the article
        research_notes: Dictionary with research notes from the underwriter
    
    Returns:
        Dictionary with newsletter blurb information
    """
    def _clean_summary_text(text):
        text = re.sub(r'\*', '', text)
        return re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\\', '')).strip()
    
    # Create newsletter blurb using the article content
    blurb_prompt = f"""
    Create a concise newsletter blurb about this article for an email newsletter.
    
    Article Title: {article_title}
    Article Content: {article_content[:2000]}
    
    Write a brief, engaging summary that:
    - Captures the key points of the article
    - Highlights why it matters to readers
    - Maintains an informative yet accessible tone
    - Implicitly encourages readers to engage with the full content
    
    Keep it under 80 tokens. Only include the blurb text itself, no introductions or meta-comments.
    """
    
    response = summary_model.generate_content(
        blurb_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=120,
            temperature=0.25
        )
    )
    
    summary = _clean_summary_text(response.text)
    
    print(f"Article Title: {article_title}")
    print(f"Summary: {summary}")
    
    return summary

def update_db(user_id, article_title, article_content, summary, people, time, topics, tags, cluster_id):
    """
    Update database with single article information.
    """
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO articles (title, user_id, cluster_id, content, summary, people, duration, topics, tags, date, completed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (article_title, user_id, cluster_id, article_content, summary, people, time, topics, tags, datetime.now(), False))

        conn.commit()
        print(f"Successfully updated articles table for user {user_id}, cluster {cluster_id}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Main Execution
def handler(payload):
    """
    Main handler function for processing a single cluster and generating an article.

    Args:
        payload: Dictionary containing user information and cluster data
    """
    user_id = payload.get("user_id")
    cluster_df = payload.get("cluster_df")  # Single cluster DataFrame
    cluster_id = payload.get("cluster_id")  # Unique identifier for this cluster
    
    print(f"Processing cluster {cluster_id} for user {user_id}")
    
    # Step 1: Underwriter researches the cluster
    research_notes = underwriter_research(cluster_df)
    
    # Step 2: Article writer creates an article for the cluster
    article = create_cluster_article(research_notes)
    
    # Step 3: Generate newsletter blurb
    summary = generate_summary(
        article['title'], 
        article['content']
    )

    topics = cluster_df['keyword'].unique().tolist()

    # Step 6: Update database
    update_db(user_id, article['title'], article['content'], summary, article['people'], article['time'], topics, article['tags'], cluster_id)
    
    print(f"Successfully processed cluster {cluster_id}")


if __name__ == "__main__":
    import pickle as pkl
    
    # Test with sample data - use first cluster as example
    cluster_df = pkl.loads(open("/tmp/cluster_dfs.pkl", "rb").read())
        
    # Step 1: Underwriter researches the cluster
    research_notes = underwriter_research(cluster_df)
    
    # Step 2: Article writer creates an article for the cluster
    article = create_cluster_article(research_notes)
    
    # Step 3: Generate newsletter blurb
    summary = generate_summary(
        article['title'], 
        article['content']
    )

    topics = cluster_df['keyword'].unique().tolist()
        
    print("---- GENERATED ARTICLE ----")
    print(f"Title: {article['title']}")
    print(f"Content: {article['content']}")
    print(f"Summary: {summary}")
    print(f"People: {article['people']}")
    print(f"Time to read: {article['time']} minutes")
    print(f"Tag: {article['tags']}")
    print(f"Topics: {topics}")
    print("\n" + "-"*50)