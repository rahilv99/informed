# set up environment variables for API keys in terminal e.g export GOOGLE_API_KEY=your_key, export OPENAI_API_KEY=your_key

import re
#Gemini stuff
import google.generativeai as genai
# merge chunks
from pydub import AudioSegment
import os
from openai import OpenAI

from logic.pulse_output import PulseOutput
import common.sqs
import common.s3

TEMP_BASE = "/tmp"

# carteisa is expensive, TTS account is currently: CLOSED
cartesia = False

GOOGLE_API_KEY= os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

summary_model = genai.GenerativeModel('gemini-1.5-flash') # 15 RPM, $0.030 /million output tokens for higher RPM
script_model = genai.GenerativeModel('gemini-2.0-flash') # 2 RPM, $5 /million output tokens for higher RPM

small_model = genai.GenerativeModel('gemini-1.5-flash-8b') # 15 RPM, $0.030 /million output tokens for higher RPM


def summarize(title, text, use = 'summary'):
    if use == 'topic':
        prompt = f"Create a informative topic label based on the title of the documents discussed. Only include the generated topic itself; avoid any introductions, explanations, or meta-comments. \
            Topics: {text}"
    if use == 'title':
        prompt = f"Create a informative and attention-grabbing title based on the topics discussed. Only include the generated title itself; avoid any introductions, explanations, or meta-comments. \
            Titles: {text}"
    else: # email header case
        prompt = f"Provide a succinct TLDR summary about the collection of articles with the topic '{title}'.\
            Highlight the key details that help the user decide whether the source is worth reading. Only include the summary itself;\
            avoid any introductions, explanations, or meta-comments. This summary will be in an email newsletter. Make the summary attention-grabbing and informative.\
            Keep it less than 80 tokens.\
            Articles: \n {text}"
    
    response = small_model.generate_content(prompt,
                                                generation_config = genai.GenerationConfig(
                                            max_output_tokens=100,
                                            temperature=0.25))
    return response.text


### Underwriter - Researches documents in a cluster
def underwriter_research(cluster_df):
    """
    Research component that analyzes documents in a cluster and creates detailed notes
    for the segment writers.
    
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
    You are a research analyst for a podcast about government documents and their impact on current events.
    
    Analyze this primary government document and create detailed research notes that will help a podcast script writer.
    
    DOCUMENT:
    Title: {primary_doc['title']}
    Text: {primary_doc['text'][1000:50000]}
    
    Create research notes with the following sections:
    1. Key Points: Main ideas and decisions in the document
    2. Important Figures: Key people, organizations, or entities mentioned
    3. Metrics & Deadlines: Any specific numbers, amounts, or timeframes
    4. Implications: Potential impact or consequences of this document
    5. Context: Historical or policy context that would help listeners understand
    
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
        You are a research analyst for a podcast about government documents and their impact on current events.
        
        Analyze this government document and create research notes that will help a podcast script writer.
        
        DOCUMENT:
        Title: {doc['title']}
        Text: {doc['text'][1000:50000]}
        
        Create research notes with the following sections:
        1. Key Points: Main ideas and decisions in the document
        2. Important Figures: Key people, organizations, or entities mentioned
        3. Metrics & Deadlines: Any specific numbers, amounts, or timeframes
        4. Implications: Potential impact or consequences of this document
        5. Context: Historical or policy context that would help listeners understand

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
        '''
        news_prompt = f"""
        You are a research analyst for a podcast about government documents and their impact on current events.
        
        Analyze this news article and create research notes that will help a podcast script writer.
        
        ARTICLE:
        Title: {article['title']}
        Publisher: {article['publisher']}
        Text: {article['text'][:30000]}
        
        Create research notes with the following sections:
        1. Key Points: Main ideas and decisions in the document
        2. Important Figures: Key people, organizations, or entities mentioned
        3. Metrics & Deadlines: Any specific numbers, amounts, or timeframes
        4. Implications: Potential impact or consequences of this document
        5. Context: Historical or policy context that would help listeners understand
        
        Format your response as a structured set of notes, not as a narrative. Be concise.
        Keep your response less than 200 tokens.
        """
        
        news_response = summary_model.generate_content(
            news_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=200,
                temperature=0.2
            )
        )
        '''
        research_notes['news_articles'].append({
            'title': article['title'],
            'publisher': article['publisher'],
            'url': article['url'],
            'notes': '' #news_response.text
        })
    
    return research_notes


### Segment writer - Creates a script for a cluster based on underwriter's research
def create_cluster_segment(research_notes, plan='free'):
    """
    Creates a podcast segment for an entire cluster based on the underwriter's research.
    
    Args:
        research_notes: Dictionary with research notes from the underwriter
        plan: 'free' or 'premium' to determine segment length
    
    Returns:
        String containing the podcast segment script
    """
    if plan == 'free':
        tokens = 200
    else:  # premium
        tokens = 250
    
    # Extract information from research notes
    primary_doc = research_notes['primary_doc']
    secondary_docs = research_notes['secondary_docs']
    news_articles = research_notes['news_articles']
    
    # Create a prompt for the segment writer
    system_prompt = f"""
    You are a professional podcast script writer for "Auxiom," a podcast that breaks down complex government documents and their impact on current events. 
    
    Your task is to write an engaging segment of a script for a text-to-speech model. This segment will feature a dialogue between **HOST 1** and **HOST 2**, discussing a topic based on government documents and news articles.
    You have been provided with research notes from a research analyst, which you will use to generate content. Do not mention these to the reader.

    **FORMAT:**
    * Mark each conversational turn with **HOST 1** or **HOST 2**.
    * This is an intermediate segment. Do not include introductions, summaries, or meta-comments. Jump directly into the dialogue.
    * Focus on explaining the core information across the documents in an engaging way.
    * Clearly attribute opinions to specific individuals.
    * Explain the potential impact of decisions made in the documents.
    
    **STRUCTURE:**
    1. Begin with a brief introduction to the topic
    2. Discuss the primary government document and its key points
    3. Mention related government documents and how they connect
    4. Discuss current news articles and how they relate to the government actions
    5. Observe implications, next steps, or reflections
    
    **SPEECH TIPS:**
    * Hosts are charismatic, professional, and genuinely interested in the topic.
    * Use short, clear sentences suitable for text-to-speech. Avoid complex phrasing, jargon, and acronyms (unless absolutely necessary and explained).
    * Aim for a natural, dynamic conversational flow.
    * Speak intelligently, with rich content and depth.
    * Incorporate filler words ("uh," "like," "you know") and occasional repetitions for a more human-like sound.
    * Create a dynamic range of responses.
    
    **Example:**
    **HOST 1:** Today we're looking at a significant development in...
    **HOST 2:** Yes, I've been following this closely. The government just released...
    **HOST 1:** Right, and what's interesting is how this connects to...
    **HOST 2:** Exactly. And we're already seeing the impact in the news...
    
    Remember: This segment must be approximately {tokens} tokens long.
    
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
def make_podcast_script(cluster_dfs, plan='free'):
    """
    Creates a complete podcast script from multiple cluster segments.
    
    Args:
        cluster_dfs: List of DataFrames, each representing a cluster
        name: Name of the podcast
        plan: 'free' or 'premium' to determine podcast length
    
    Returns:
        Complete podcast script
    """
    if plan == 'plus':
        tokens = 1500
        cluster_dfs = cluster_dfs[:5]
    else:  # free
        tokens = 900
        # Limit to 3 clusters for free plan
        cluster_dfs = cluster_dfs[:3]
    
    # Process each cluster
    segments = []
    notes = []
    for i, cluster_df in enumerate(cluster_dfs):
        print(f"Processing cluster {i+1}/{len(cluster_dfs)}")
        
        # Step 1: Underwriter researches the cluster
        research_notes = underwriter_research(cluster_df)
        
        # Step 2: Segment writer creates a script for the cluster
        segment = create_cluster_segment(research_notes, plan)
        segments.append(segment)

        # Save notes for newsletter summaries
        notes.append(research_notes)
    
    print(f'Processed {len(segments)} clusters')
    
    # Step 3: Senior editor combines segments
    system_prompt = f"""
    You are a senior editor for a podcast "Auxiom," a podcast that breaks down complex government documents and their impact on current events. 
    
    Your task is to take the segments written by other agents, refine their content, and merge them into a consistent flow.
    
    INPUT:
    - Your agents have written multiple segments, each covering a different topic cluster
    - The scripts should be marked with **HOST 1** and **HOST 2** for each conversational turn
    - Make the output conversation {tokens} tokens long.
    
    TASK:
    - Merge the components, ensure the format of **HOST 1** and **HOST 2** is consistent
    - Refine the content to be more engaging
    - Ensure the tone and style is consistent
    - Allow each segment an equal amount of time
    - Add smooth transitions between topics
    - CLOSE WITH: 'Thanks for listening, stay tuned for more episodes.'
    
    SPEECH TIPS:
    - Since this is for a text-to-speech model, use short sentences, omit any non-verbal cues, complex sentences/phrases, or acronyms.
    
    Example: 
    **HOST 1**: Welcome to Auxiom! Today we're covering several important developments...
    **HOST 2**: That's right. The government has just...
    **HOST 1**: [First segment content]
    **HOST 2**: [First segment content]
    ...
    **HOST 1**: Now, let's move on to our next topic...
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
    
    return response.text, notes

def generate_email_headers(research_notes):
    """
    Generates email headers and descriptions for a podcast based on research notes from underwriters.
    
    Args:
        research_notes: List of dictionaries containing research notes for each cluster
    
    Returns:
        DataFrame with email descriptions and episode title
    """
    def _clean_summary_text(text):
        text = re.sub(r'\*', '', text)
        return re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\\', '')).strip()
    
    # Create a DataFrame with primary government documents
    cluster_descriptions = []
    titles = []
    
    for i, cluster_notes in enumerate(research_notes):
        # Collect titles for cluster title generation
        cluster_title_parts = []
        cluster_description_parts = []
        gov = []
        news = []

        primary_doc = cluster_notes['primary_doc']
        cluster_title_parts.append(primary_doc['title'])
        cluster_description_parts.append( f"Primary Document: {primary_doc['title']}\nNotes: {primary_doc['notes'][:2000]}")
        gov.append((primary_doc['title'], primary_doc['url']))

        # Add secondary document titles
        for doc in cluster_notes['secondary_docs']:
            cluster_title_parts.append(doc['title'])
            cluster_description_parts.append(f"Secondary Document: {doc['title']}\nNotes: {doc['notes'][:1000]}")
            gov.append((doc['title'], doc['url']))
        
        # Add news article titles
        for article in cluster_notes['news_articles']:
            cluster_title_parts.append(article['title'])
            cluster_description_parts.append(f"News Article: {article['title']} by {article['publisher']}\nNotes: {article['notes'][:1000]}")
            news.append((article['title'], article['publisher'], article['url']))

        # Create cluster title
        cluster_title_text = ", ".join(cluster_title_parts)
        cluster_title = summarize("", cluster_title_text, use='topic')
        cluster_title = _clean_summary_text(cluster_title)
        
        # Create cluster description
        cluster_description_text = "\n\n".join(cluster_description_parts)
        cluster_description = summarize(cluster_title, cluster_description_text, use='summary')
        cluster_description = _clean_summary_text(cluster_description)

        cluster_descriptions.append({
            'title': cluster_title,
            'description': cluster_description,
            'gov' : gov,
            'news': news
        })
        titles.append(cluster_title)

    # Generate episode title from cluster titles
    cluster_titles_text = ", ".join(titles)
    episode_title = summarize("", cluster_titles_text, use='title')
    episode_title = _clean_summary_text(episode_title)

    return cluster_descriptions, episode_title


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


def create_conversational_podcast(cluster_dfs, plan='free', testing = False):
    """
    Creates a conversational podcast from cluster dataframes.
    
    Args:
        cluster_dfs: List of DataFrames, each representing a cluster
        name: Name of the podcast
        plan: 'free' or 'premium' to determine podcast length
    
    Returns:
        Number of conversational turns in the podcast
    """
    # Generate the script
    script, notes = make_podcast_script(cluster_dfs, plan)
    
    # Clean the script for TTS
    turns = clean_text_for_conversational_tts(script)
    
    if testing:
        return turns, notes

    # Create audio files for each turn
    if cartesia:
        client = Cartesia(api_key=os.environ.get('CARTESIA_API_KEY'))
    else:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    for index, sentence in enumerate(turns):
        host = 1 if index % 2 == 0 else 2
        
        # handle lines longer than API limit
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
    
    return len(turns), notes


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
                model="tts-1",
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
    final_audio = intro_music.append(final_audio, crossfade=1000)
    
    print("Intro music added.")
    final_audio.export(f"{TEMP_BASE}/podcast.mp3", format="mp3")
    print(f"Conversation audio file saved as {TEMP_BASE}/podcast.mp3")
    
    # Export the final audio
    common.s3.save(user_id, episode_number, "PODCAST", f"{TEMP_BASE}/podcast.mp3")
    
    print("Audio file uploaded to S3.")


# Main Execution
def handler(payload):
    """
    Main handler function for the podcast generation process.
    
    Args:
        payload: Dictionary containing user information and preferences
    """
    user_id = payload.get("user_id")
    user_email = payload.get("user_email")
    plan = payload.get("plan")
    episode = payload.get("episode")
    ep_type = payload.get("ep_type")
    user_name = payload.get("user_name")

    pulse = PulseOutput(user_id, episode)
    all_data = pulse.all_data    

    num_turns, notes = create_conversational_podcast(all_data, plan = plan)

    write_to_s3(num_turns, user_id, episode)

    topics, episode_title = generate_email_headers(notes)

    # Save the email description to S3
    common.s3.save_serialized(user_id, episode, "EMAIL", {
        "topics": topics,
        "episode_title": episode_title
    })


    # Send message to SQS
    try:
        next_event = {
            "action": "e_email",
            "payload": {
                "user_id": user_id,
                "user_email": user_email,
                "episode": episode,
                "ep_type": ep_type,
                "user_name": user_name
            }
        }
        common.sqs.send_to_sqs(next_event)
        print(f"Sent message to SQS for next action {next_event['action']}")
    except Exception as e:
        print(f"Exception when sending message to SQS {e}")

if __name__ == "__main__":
    import pickle as pkl
    all_data = pkl.loads(open("/tmp/cluster_dfs.pkl", "rb").read())

    all_data = all_data[:3]

    num_turns, notes = create_conversational_podcast(all_data, plan = 'free', testing = True)

    topics, episode_title = generate_email_headers(notes)

    print("---- NOTES ----")
    for note in notes:
        print(f"Primary Document: {note['primary_doc']['title']}")
        print(note['primary_doc']['notes'])
        for sec in note['secondary_docs']:
            print(f"Secondary Document: {sec['title']} - {sec['url']}")
            print(sec['notes'])
    
    print(f"Episode Title: {episode_title}")

    for topic in topics:
        print(f"Title: {topic['title']}")
        print(f"Description: {topic['description']}\n")
        for gov in topic['gov']:
            print(f"Gov Document: {gov[0]} - {gov[1]}")
        for news in topic['news']:
            print(f"News Article: {news[0]} by {news[1]} - {news[2]}")