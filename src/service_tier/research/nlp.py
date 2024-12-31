
# set up environment variables for API keys in terminal e.g export GOOGLE_API_KEY=your_key, export OPENAI_API_KEY=your_key

import pandas as pd
import re
import time
#Gemini stuff
import google.generativeai as genai
# merge chunks
from pydub import AudioSegment
import os
from openai import OpenAI

import time
from threading import Lock



GOOGLE_API_KEY= os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

summary_model = genai.GenerativeModel('gemini-1.5-flash') # 15 RPM, $0.030 /million output tokens for higher RPM
script_model = genai.GenerativeModel('gemini-1.5-pro') # 2 RPM, $5 /million output tokens for higher RPM

# implement counters to ensure we are below rate limits
# Global rate-limit counters and locks
summary_model_counter = 0
summary_model_lock = Lock()
script_model_counter = 0
script_model_lock = Lock()

# Timestamps to track last reset
time_last_reset_summary_model = time.time()
time_last_reset_script_model = time.time()

# Rate limit configurations
SUMMARY_MODEL_RPM_LIMIT = 15
SCRIPT_MODEL_RPM_LIMIT = 2

# Function to enforce rate limits
def enforce_rate_limit(model_name):
    global summary_model_counter, script_model_counter
    global time_last_reset_summary_model, time_last_reset_script_model

    current_time = time.time()

    if model_name == "summary_model":
        with summary_model_lock:
            elapsed_time = current_time - time_last_reset_summary_model

            if elapsed_time >= 60:  # Reset every minute
                summary_model_counter = 0
                time_last_reset_summary_model = current_time

            if summary_model_counter >= SUMMARY_MODEL_RPM_LIMIT:
                wait_time = 60 - elapsed_time
                print(f"Rate limit reached for summary_model. Waiting for {wait_time:.2f} seconds.")
                time.sleep(wait_time)
                summary_model_counter = 0
                time_last_reset_summary_model = time.time()

            summary_model_counter += 1

    elif model_name == "script_model":
        with script_model_lock:
            elapsed_time = current_time - time_last_reset_script_model

            if elapsed_time >= 60:  # Reset every minute
                script_model_counter = 0
                time_last_reset_script_model = current_time

            if script_model_counter >= SCRIPT_MODEL_RPM_LIMIT:
                wait_time = 60 - elapsed_time
                print(f"Rate limit reached for script_model. Waiting for {wait_time:.2f} seconds.")
                time.sleep(wait_time)
                script_model_counter = 0
                time_last_reset_script_model = time.time()

            script_model_counter += 1

# Wrap API calls to enforce rate limits
def summarize_with_rate_limit(title, text, use='summary', type='secondary'):
    enforce_rate_limit("summary_model")
    return summarize(title, text, use, type)

def make_script_with_rate_limit(summaries, titles, name, plan='free', type='pulse'):
    enforce_rate_limit("script_model")
    return make_script(summaries, titles, name, plan, type)


def summarize(title, text, use = 'summary', type = 'secondary'):
  if type == 'secondary':
      tokens = 400
  elif type == 'primary':
      tokens = 800
  else:
      tokens = 100 # email title + summaries
    
  if use == 'summary':
    prompt = f"Create a summary of the overall goal, methods, and results of the article titled '{title}'.\
        Be sure to get all important information including the limitations where applicable. Your response should be at least {tokens-200} tokens \
        Keep notes about the details of the article, including a header of the title.: {text}"
  elif use == 'title':
    prompt = f"Create a title for the podcast based on the title of the academic articles discussed. The title should be attention-grabbing, professional, and informative.\
                Only include the generated title itself; avoid any introductions, explanations, or meta-comments. This generated title will be in an email newsletter.\
        Titles: {text}"
  else: # email header case
    prompt = f"Provide a succinct TLDR summary about the academic article titled '{title}'.\
        Highlight the key details that help the user decide whether the source is worth reading. Only include the summary itself;\
        avoid any introductions, explanations, or meta-comments. This summary will be in an email newsletter. Make the summary attention-grabbing and informative.\
        Text: {text}"
    
  response = summary_model.generate_content(prompt,
                                            generation_config = genai.GenerationConfig(
                                        max_output_tokens=tokens,
                                        temperature=0.25))
  return response

def make_script(summaries, titles, name, plan = 'free', type = 'pulse'):
    if type == 'pulse':
        additional_text = ''
    elif type == 'insight':
            additional_text = f'- The first article is the primary focus of this episode. We will explore the details of this article the most in depth, writing mostly about this. \
                The second and third article have cited the first article, demonstrating the application of the 1st research. Discuss the 1st article in depth, finding how the other article(s) have applied the 1st.\
                Only include information from the other articles that are direct applications of the first article. \n'
    

    if plan == 'plus':
        tokens = 3000
        summaries = summaries
    else: # free
        tokens = 1500
        summaries = summaries[:2]
        additional_text = 'At the end of the podcast, tell the user they can subscribe to our premium plan for more in-depth analyses and longer podcasts. \n'
    
    if type == 'insight':
        tokens = 1500

    system_prompt =f"""
    Act as a professional podcast script writer for a podcast Auxiom. Your task is to create a script to be sent to a text-to-speech model where **HOST 1** is asking questions, and **HOST 2** explains using the summaries of articles below.
    - Mark the script with **HOST 1** and **HOST 2** for each conversational turn
    - The speakers should minimize referring to each other. If they must, HOST 1 = Mia and HOST 2 = Leo
    - Always maintain the names of the hosts and their order. HOST 1 is always Mia, HOST 2 is always Leo.
    - Create a sequence, exploring the details of each article one by one
    - Extract as much substance (main points, results, methods, goals) from the article as possible
    - The hosts should be critical if the article has limitations
    - These hosts are charismatic and professional. They are excited about the information.
    - Make the conversation at least {tokens} tokens long.
    - Since this is for a text-to-speech model, use short sentences, omit any non-verbal cues, and don't use complex sentences/phrases.
    - Include filler words like 'uh' or repeat words in many of the sentences to make the conversation more natural.
    - Use specific details from the text relevant to the goals, methods, and results
    - Close with 'Thanks for listening, stay tuned for more episodes.'
    - This is custom made for one listener named {name}, greet them at the beginning of the episode.
    
    {additional_text}
    Example: 
    **HOST 1**: Today we have an article about X...
    **HOST 2 **: That's right, Mia. The article discusses Y...
    **HOST 1**: Leo, how does this article relate to Z?

    Remember: This script must be at least {tokens} tokens long. Do not produce fewer.

Articles: """
    for i in range(len(summaries)):
        system_prompt += f" Article {i} - {titles[i]}: {summaries[i]}"        

    response = script_model.generate_content(system_prompt, 
                                      generation_config = genai.GenerationConfig(
                                        max_output_tokens=tokens+500,
                                        temperature=0.25))
    if plan == 'pro' or plan == 'plus':
        response = review_script(response, tokens)
    
    return response

def review_script(script, tokens = 2500):
    prompt = f"Review the script for the podcast episode, making it sound very human-like. Refine any wording that may be difficult for a text-to-speech model. Make sure the content flows well and is engaging.\
        Retain the structure, including the conversational turns between the hosts. Remove or replace acronyms where necessary. Do not add any unecessary phrases as this will be fed directly to a text-to-speech model.\
        Script: {script}"
    response = script_model.generate_content(prompt, generation_config = genai.GenerationConfig(
                                        max_output_tokens=tokens+500,
                                        temperature=0.15))
    return response

def generate_script(all_data, name, plan = 'free', type = 'pulse'):
    for index, row in all_data.iterrows():
        title = row['title']
        text = row['text']

        if type == 'insight' and index == 0:
            article = 'primary' # extended summary for first article in deep dive (primary article)
        else:
            article = 'secondary'

        summary = summarize_with_rate_limit(title, text, use = 'summary', type = article)
        all_data.at[index, 'summary'] = summary.text

    # generate script
    summaries = all_data['summary'].tolist()
    titles = all_data['title'].tolist()
    script = make_script_with_rate_limit(summaries, titles, name, plan, type)
    return script.text

def generate_email_headers(all_data, plan = 'free', type = 'pulse'):
    def clean_summary_text(text):
        text = re.sub(r'\*', '', text)
        return re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\\', '')).strip()
    if plan == 'free':
        all_data = all_data.head(2)

    podcast_description = all_data[['title', 'url', 'summary']].copy()

    podcast_description['description'] = podcast_description.apply(
        lambda row: clean_summary_text(summarize_with_rate_limit(row['title'], row['summary'], use='email').text),
        axis=1)
    podcast_description.drop(columns=['summary'], inplace=True)
    
    titles = podcast_description['title'].tolist()
    if type == 'insight':
        titles = titles[0]
    else:
        titles = ", ".join(titles)
    episode_title = summarize_with_rate_limit("", titles, use = 'title')

    return podcast_description, episode_title.text

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
        # Remove (Aria): and (Theo): if exist
        ret = statement.replace('(Leo):', '').replace('(Mia):', '')

        # Replace '\n' with a space
        ret = ret.replace('\n', ' ')
        # remove '& 1' or '& 2'
        ret = re.sub(r'& \d', '', ret)
        # Remove Markdown-style (*)
        ret = re.sub(r'\*\*\:', '', ret)
        ret = re.sub(r'\*', '', ret)
        # Ensure no extra spaces
        ret = re.sub(r'\s+', ' ', ret).strip()
        
        output_text.append(ret)

    print(output_text)
    return output_text

def create_conversational_podcast(all_data, name, plan='free', type='pulse'):

    def _create_line(client, host, line, num, chunk):

        if host == 1:
            # female
            voice = 'nova'
        else: # host = 2
            # male
            voice = 'onyx'

        output_file = f"data/conversation/{host}/line_{num}_{chunk}.mp3"

         # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            response = client.audio.speech.create(
                model="tts-1", # (use "tts-1" or "tts-1-hd")
                voice=voice,
                input=line
            )

            # Save the response content (audio) to a file
            with open(output_file, "wb") as audio_file:
                audio_file.write(response.content)

            print(f"Audio file saved as {output_file}")

        except Exception as e:
            print(f"An error occurred while generating TTS: {e}")

    # Instantiates a client
    script = generate_script(all_data, name, plan=plan, type=type)
    turns = clean_text_for_conversational_tts(script)

    key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=key)

    for index, sentence in enumerate(turns):
        host = 1 if index % 2 == 0 else 2

        # handle lines longer than API limit
        if len(sentence) > 4096:
            # Chunk into 4096 characters
            chunks = [sentence[i:i + 4096] for i in range(0, len(sentence), 4096)]

            for chunk_index, chunk in enumerate(chunks):
                _create_line(client, host, chunk, index, chunk_index)

            chunk_files = [f"data/conversation/{host}/line_{index}_{i}.mp3" for i in range(len(chunks))]
            combined_audio = AudioSegment.empty()
            for file in chunk_files:
                audio_segment = AudioSegment.from_mp3(file)
                combined_audio += audio_segment

            combined_output_file = f"data/conversation/{host}/line_{index}_0.mp3"
            combined_audio.export(combined_output_file, format="mp3")

            # Clean up individual chunk files
            for file in chunk_files:
                os.remove(file)

        else:
            _create_line(client, host, sentence, index, 0)

        time.sleep(60 / 500)  # rate limit = 500 requests per minute

    # merge audio files
    # Create a new AudioSegment object
    final_audio = AudioSegment.from_mp3('data/conversation/1/line_0_0.mp3')
    for i in range(1, len(turns)):
        audio = AudioSegment.from_mp3(f"data/conversation/{1 if i % 2 == 0 else 2}/line_{i}_0.mp3")
        # clean up
        os.remove(f"data/conversation/{1 if i % 2 == 0 else 2}/line_{i}_0.mp3")

        final_audio = final_audio.append(audio)

    # add intro music
    intro_music = AudioSegment.from_file("data/intro_music.mp3")
    final_audio = intro_music.append(final_audio, crossfade=1000)

    # Export the final audio
    final_audio.export("data/conversation/final_conversation.mp3", format="mp3")
    print("Conversation audio file saved as data/conversation/final_conversation.mp3")




if __name__ == "__main__":
    all_data = pd.read_csv('./data/recommended_papers.csv')
    name = 'Rahil'

    create_conversational_podcast(all_data, name, plan = 'plus', type = 'pulse')

    email_description, episode_title = generate_email_headers(all_data, plan = 'plus', type = 'insight')
    email_description.to_csv('./data/email_description.csv', index = False)