# set up environment variables for API keys in terminal e.g export GOOGLE_API_KEY=your_key, export OPENAI_API_KEY=your_key

import re
#Gemini stuff
import google.generativeai as genai
# merge chunks
from pydub import AudioSegment
import os
from openai import OpenAI
import psycopg2 
import json
from datetime import datetime

import common.s3

db_access_url = os.environ.get('DB_ACCESS_URL')
TEMP_BASE = "/tmp"

# carteisa is expensive, TTS account is currently: CLOSED
cartesia = False

GOOGLE_API_KEY= os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

summary_model = genai.GenerativeModel('gemini-2.0-flash') # $0.075 /M input  $0.30 /M output tokens 
script_model = genai.GenerativeModel('gemini-2.5-flash') # $0.10 /M input $0.40 /M output tokens

def summarize(title, text, use = 'summary'):
    if use == 'topic':
        prompt = f"Create a informative topic title based on the title of the documents discussed. Only include the generated title itself; avoid any introductions, explanations, or meta-comments. \
            Titles: "
        for i, title in enumerate(text):
            prompt += f"Article {i}: {title}, "
    if use == 'title':
        prompt = f"Create a informative and attention-grabbing title based on the topics discussed. Only include the generated title itself; avoid any introductions, explanations, or meta-comments. \
            Titles: "
        for i, title in enumerate(text):
            prompt += f"Article {i}: {title}, "
    if use == 'summary':
        prompt = f"Provide a succinct summary about the collection of articles with the topic '{title}'.\
            Highlight the key details. Structure your output as a simple plain text response with only english characters. Only include the summary itself;\
            avoid any introductions, explanations, or meta-comments. This summary will go directly into an email newsletter. Make the summary attention-grabbing and informative.\
            Keep it less than 80 tokens.\
            Articles: \n {text}"
    
    response = summary_model.generate_content(prompt,
                                                generation_config = genai.GenerationConfig(
                                            max_output_tokens=120,
                                            temperature=0.25))
    return response.text


def clean_text_for_conversational_tts(input_text):
    """
    Cleans text for Text-to-Speech by:
    - Replacing '\n' with spaces.
    - Removing Markdown-style formatting like '**bold**'.
    """
    # Match and extract statements for both HOST 1 and HOST 2.
    pattern = r"HOST [12]([^\n]+)"
    statements = re.findall(pattern, input_text)
    
    output_text = []
    for statement in statements:
        # Remove :
        statement = statement.replace(':', '')
        # Replace '\n' with a space
        statement = statement.replace('\n', ' ')
        # remove '& 1' or '& 2'
        statement = re.sub(r'& \d', '', statement)
        # Remove Markdown-style (*)
        statement = re.sub(r'\*\*\:', '', statement)
        statement = re.sub(r'\*', '', statement)
        # Ensure no extra spaces
        statement = re.sub(r'\s+', ' ', statement).strip()
        
        if statement != '':
            output_text.append(statement)
    
    print(output_text)
    return output_text


def _create_line(client, host, line, num, chunk):
    """
    Creates an audio line for a specific host.
    
    Args:
        client: TTS client
        host: Host number (1 or 2)
        line: Text to convert to speech
        num: Line number
        chunk: Chunk number (for long lines)
    """
    if host == 1:
        # female
        if cartesia:
            voice = '156fb8d2-335b-4950-9cb3-a2d33befec77'
        else:
            voice = 'nova'
    else:  # host = 2
        # male
        if cartesia:
            voice = '729651dc-c6c3-4ee5-97fa-350da1f88600'
        else:
            voice = 'onyx'
    
    output_file = f"{TEMP_BASE}/conversation/{host}/line_{num}_{chunk}.mp3"
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        if cartesia:
            audio_bytes = client.tts.bytes(
                model_id="sonic-english",
                transcript=line,
                voice_id=voice,
                language="en",
                output_format={
                    "container": "wav",
                    "sample_rate": 44100,
                    "encoding": "pcm_s16le",
                },
            )
        else:
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=line,
                response_format='mp3'
            )
            response.stream_to_file(output_file)
    
    except Exception as e:
        print(f"An error occurred while generating TTS: {e}")


def write_to_s3(num_turns, user_id, episode_number):
    """
    Writes the podcast audio to S3.
    
    Args:
        num_turns: Number of conversational turns
        user_id: User ID
        episode_number: Episode number
    """
    # merge audio files
    print("Merging audio files...")
    
    final_audio = AudioSegment.from_mp3(f"{TEMP_BASE}/conversation/1/line_0_0.mp3")
    for i in range(1, num_turns):
        audio = AudioSegment.from_mp3(f"{TEMP_BASE}/conversation/{1 if i % 2 == 0 else 2}/line_{i}_0.mp3")
        final_audio = final_audio.append(audio)
    
    print("Audio files merged.")
    
    # add intro music
    # Load the intro music from s3
    common.s3.restore_from_system("INTRO", f"{TEMP_BASE}/intro_music.mp3")
    
    intro_music = AudioSegment.from_mp3(f"{TEMP_BASE}/intro_music.mp3")
    final_audio = intro_music.append(final_audio, crossfade=2000)
    
    print("Intro music added.")
    final_audio.export(f"{TEMP_BASE}/podcast.mp3", format="mp3")
    print(f"Conversation audio file saved as {TEMP_BASE}/podcast.mp3")
    
    # Export the final audio
    common.s3.save(user_id, episode_number, "PODCAST", f"{TEMP_BASE}/podcast.mp3")
    
    print("Audio file uploaded to S3.")

def update_db(user_id, episode_title, topics, episode_number, s3_url, script):
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO podcasts (title, user_id, articles, episode_number, audio_file_url, script, date, completed)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s)
            RETURNING id
        """, (episode_title, user_id, json.dumps(topics), episode_number, s3_url, json.dumps(script), datetime.now(), False))
        

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

# Main Execution
def get_articles_from_db(article_ids):
    """
    Retrieve articles from the database using article IDs.
    
    Args:
        article_ids: List of article IDs to retrieve
    
    Returns:
        List of article dictionaries with title, content, summary, etc.
    """
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        # Create placeholders for the IN clause
        placeholders = ','.join(['%s'] * len(article_ids))
        
        cursor.execute(f"""
            SELECT id, title, content, summary, topics, tags
            FROM articles 
            WHERE id IN ({placeholders})
        """, article_ids)
        
        articles = []
        for row in cursor.fetchall():
            
            articles.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'summary': row[3],
                'topics': row[4],
                'tags': row[5],
                'url': f"https://auxiomai.com/article/{row[0]}"
            })
        
        print(f"Retrieved {len(articles)} articles from database")
        return articles
        
    except psycopg2.Error as e:
        print(f"Database error retrieving articles: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


### Segment writer - Creates a script segment for an individual article
def create_article_segment(article, plan='free'):
    """
    Creates a podcast segment for an individual article.
    
    Args:
        article: Article dictionary with keys: 'id', 'title', 'content', 'summary', 'topics', 'tags', 'url'
        plan: 'free' or 'premium' to determine segment length
    
    Returns:
        String containing the podcast segment script
    """
    if plan == 'free':
        tokens = 400
    else:  # premium
        tokens = 500
    
    # Create a prompt for the segment writer
    system_prompt = f"""
    You are a professional podcast script writer for "Auxiom," a podcast that discusses articles published on our website and their impact on current events.
    
    Your task is to write an engaging segment of a script for a text-to-speech model. This segment will feature a dialogue between **HOST 1** and **HOST 2**, discussing a single article from our website.

    **FORMAT:**
    * Mark each conversational turn with **HOST 1** or **HOST 2**.
    * This is an intermediate segment. Do not include introductions, summaries, or meta-comments. Jump directly into the dialogue.
    * Focus on explaining the core information from the article in an engaging way.
    * Clearly reference the article and its key points.
    * Explain the potential impact and implications discussed in the article.
    
    **STRUCTURE:**
    1. Begin with a brief introduction to the article's topic
    2. Discuss the article's key points and insights
    3. Explore the implications and broader context
    4. Conclude with reflections or next steps
    
    **SPEECH TIPS:**
    * Hosts are charismatic, professional, and genuinely interested in the topic.
    * Use short, clear sentences suitable for text-to-speech. Avoid complex phrasing, jargon, and acronyms (unless absolutely necessary and explained).
    * Aim for a natural, dynamic conversational flow.
    * Speak intelligently, with rich content and depth.
    * Incorporate filler words ("uh," "like," "you know") and occasional repetitions for a more human-like sound.
    * Create a dynamic range of responses.
    
    **Example:**
    **HOST 1:** Today we're looking at a significant development in...
    **HOST 2:** Yes, I've been following this closely. Our latest article just covered...
    **HOST 1:** Right, and what's interesting is how this connects to...
    **HOST 2:** Exactly. And we're already seeing the impact in...
    
    Remember: This segment must be approximately {tokens} tokens long.
    
    **ARTICLE:**
    Title: {article['title']}
    Content: {article.get('content', article.get('summary', ''))}
    Topics: {', '.join(article.get('topics', []))}
    """
    
    # Generate the segment
    response = script_model.generate_content(
        system_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=tokens*2,
            temperature=0.3
        )
    )
    
    return response.text


### Senior editor - Combines segments into a cohesive podcast
def make_podcast_script(articles, plan='free'):
    """
    Creates a complete podcast script from individual articles.
    
    Args:
        articles: List of article dictionaries
        plan: 'free' or 'premium' to determine podcast length
    
    Returns:
        Complete podcast script
    """
    if plan == 'paid':
        tokens = 900
        # Limit articles for free plan
        articles = articles[:3]
    else:  # premium
        tokens = 2000
        articles = articles[:5]
    
    # Process each article to create segments
    segments = []
    for i, article in enumerate(articles):
        print(f"Processing article {i+1}/{len(articles)}: {article['title']}")
        
        # Segment writer creates a script for each article
        segment = create_article_segment(article, plan)
        segments.append(segment)
    
    print(f'Processed {len(segments)} article segments')
    
    # Senior editor combines segments
    system_prompt = f"""
    You are a senior editor for a podcast "Auxiom," a podcast that discusses articles published on our website and their impact on current events.
    
    Your task is to take the segments written by other agents, refine their content, and merge them into a consistent flow.
    
    INPUT:
    - Your agents have written multiple segments, each covering a different article
    - The scripts should be marked with **HOST 1** and **HOST 2** for each conversational turn
    - Make the output conversation {tokens} tokens long.
    
    TASK:
    - Merge the components, ensure the format of **HOST 1** and **HOST 2** is consistent
    - Refine the content to be more engaging
    - Ensure the tone and style is consistent
    - Allow each segment an equal amount of time
    - Add smooth transitions between articles
    - Start with a brief welcome and introduction to the episode
    - CLOSE WITH: 'Thanks for listening, stay tuned for more episodes.'
    
    SPEECH TIPS:
    - Since this is for a text-to-speech model, use short sentences, omit any non-verbal cues, complex sentences/phrases, or acronyms.
    
    Example: 
    **HOST 1**: Welcome to Auxiom! Today we're covering several important articles from our website...
    **HOST 2**: That's right. We have some fascinating stories to discuss...
    **HOST 1**: [First segment content]
    **HOST 2**: [First segment content]
    ...
    **HOST 1**: Now, let's move on to our next article...
    **HOST 2**: Yes, this is another significant development...
    **HOST 1**: [Second segment content]
    **HOST 2**: [Second segment content]
    ...
    **HOST 1**: Finally, let's discuss...
    **HOST 2**: This is particularly interesting because...
    **HOST 1**: [Third segment content]
    **HOST 2**: [Third segment content]
    ...
    **HOST 1**: We hope you've learned something new today. Thanks for listening, stay tuned for more episodes.
    
    Remember: This segment must be approximately {tokens} tokens long.
    
    SEGMENTS:
    """
    
    # Add all segments to the prompt
    for i, segment in enumerate(segments):
        system_prompt += f"\n\nSEGMENT {i+1}:\n{segment}\n"
    
    # Generate the complete podcast script
    response = script_model.generate_content(
        system_prompt,
        generation_config=genai.GenerationConfig(
            max_output_tokens=tokens*2,
            temperature=0.15
        )
    )
    
    return response.text


def create_podcast_from_articles(articles, plan="paid"):
    """
    Creates a podcast script using the segment writer + senior writer architecture.
    
    Args:
        articles: List of article dictionaries
        plan: 'free' or 'premium' to determine podcast length
    
    Returns:
        Tuple of (script_turns, episode_title)
    """
    if plan == 'paid':
        # Limit articles for paid plan
        articles = articles[:3]
    else:  # premium
        articles = articles[:5]
    
    # Generate the script using the new architecture
    script = make_podcast_script(articles, plan)
    
    # Clean the script for TTS
    turns = clean_text_for_conversational_tts(script)
    
    # Generate episode title from article titles
    article_titles = [article['title'] for article in articles]
    episode_title = summarize("", article_titles, use='title')
    episode_title = re.sub(r'\*', '', episode_title)
    episode_title = re.sub(r'\s+', ' ', episode_title.replace('\n', ' ').replace('\\', '')).strip()
    
    return turns, episode_title


def handler(payload):
    """
    Main handler function for the podcast generation process.

    Args:
        payload: Dictionary containing user information and article recommendations
    """
    user_id = payload.get("user_id")
    plan = payload.get("plan")
    episode = payload.get("episode")
    recommendations = payload.get("recommendations", [])

    print(f"Processing podcast for user {user_id}, episode {episode}")
    print(f"Article recommendations: {recommendations}")

    # Get articles from database using the recommendation IDs
    articles = get_articles_from_db(recommendations)
    
    if not articles:
        print("No articles found for the given recommendations")
        return
    
    # Create podcast script using the new segment writer + senior writer architecture
    script_turns, episode_title = create_podcast_from_articles(articles, plan)
    
    # Create TTS audio files
    if cartesia:
        client = Cartesia(api_key=os.environ.get('CARTESIA_API_KEY'))
    else:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    for index, sentence in enumerate(script_turns):
        host = 1 if index % 2 == 0 else 2
        
        # Handle lines longer than API limit
        if len(sentence) > 4096:
            # Chunk into 4096 characters
            chunks = [sentence[i:i + 4096] for i in range(0, len(sentence), 4096)]
            
            for chunk_index, chunk in enumerate(chunks):
                _create_line(client, host, chunk, index, chunk_index)
            
            chunk_files = [f"{TEMP_BASE}/conversation/{host}/line_{index}_{i}.mp3" for i in range(len(chunks))]
            combined_audio = AudioSegment.empty()
            for file in chunk_files:
                audio_segment = AudioSegment.from_mp3(file)
                combined_audio += audio_segment
            
            print(f"Combined chunked audio for line {index}")
            combined_output_file = f"{TEMP_BASE}/conversation/{host}/line_{index}_0.mp3"
            combined_audio.export(combined_output_file, format="mp3")
            
            # Clean up individual chunk files
            for file in chunk_files:
                os.remove(file)
        else:
            _create_line(client, host, sentence, index, 0)
    
    # Save audio file to S3
    num_turns = len(script_turns)
    write_to_s3(num_turns, user_id, episode)
    
    # Get S3 URL for the saved audio
    s3_url = common.s3.get_s3_url(user_id, episode, "PODCAST")
    
    # Update database with podcast information
    article_info = [{"title": article['title'], "description": article["summary"], "url": article['url']} for article in articles]
    update_db(user_id, episode_title, article_info, episode, s3_url, script_turns)
    
    print(f"Podcast generation completed for user {user_id}, episode {episode}")






if __name__ == "__main__":
    # Test the new functionality
    test_payload = {
        "user_id": "test_user",
        "plan": "free",
        "episode": 1,
        "ep_type": "regular",
        "recommendations": [1, 2, 3]  # Example article IDs
    }
    
    print("Testing new podcast generation from article recommendations...")
    handler(test_payload)
