# Invoked with a single new bill event. Extracts key events from bill, processes and stores in database

from google import genai
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.database as database
import json
import numpy as np
import uuid
import anthropic

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
genai_client = genai.Client(api_key=GOOGLE_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

uri = os.environ.get("DB_URI", "mongodb+srv://admin:astrapodcast!@auxiom-backend.7edkill.mongodb.net/?retryWrites=true&w=majority&appName=auxiom-backend")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']
events_collection = db['events']


def get_events(bill):
    system_prompt = """You are an expert legislative analyst. Your task is to extract policy events from the text of a U.S. legislative bill.

Definition of an event:
One or more spans of bill text that constitutes a change in policy for one or more topics.
Must include enough context to determine what the change is and what it applies to.
All details related to the event should be encapsulated in the group of spans.
Each individual event must be different from the other events in the bill.

For each event, return a JSON object in the following format:
{
"text": "<exact span of bill text describing the policy change>",
"topics": ["<broad policy areas impacted>"],
"tags": ["<specific descriptors within the topics>"],
"summary": "<shortened version of text highlighting main idea of event>",
"title": "<concise descriptor of event>"
}

Guidelines:
- Topics are broad policy areas where the U.S. government takes a stance (e.g., "Healthcare", "Defense", "Education", "Energy", "Immigration").
- Tags are narrower descriptors that specify the scope within a topic (e.g., for Healthcare → "Medicare", "drug pricing"; for Energy → "renewable energy", "oil subsidies")
- Summaries are a concise overview of the event with necessary context on the bill. It will be viewed outside of the context of the bill.
- Extract all unique events in the bill. Each event must be completely different from the other events. Merge similar events.
- There is no minimum or maximum number of events. Be sure all events meet the requirements outlined. 
- Prune events that are simply minor, technical, or procedural details of the bill (such as budget scoring rules, effective dates, definitions, or clerical amendments). Only include substantive policy changes that affect how government programs, funding, or regulations actually operate.
- Only output valid JSON as a list of objects (no commentary, no explanation).

Example output:
[
    {
        "text": "Notwithstanding any other provision of law, the Secretary of Health and Human Services shall, beginning on January 1, 2026, negotiate directly with manufacturers of insulin products with respect to the prices that may be charged to prescription drug plans under part D of title XVIII of the Social Security Act for such products furnished to individuals entitled to benefits under such title.",
        "topics": ["Healthcare"],
        "tags": ["Medicare", "drug pricing", "insulin"],
        "summary": "The Secretary of Health and Human Services will negotiate the price of insulin for Medicare beneficiaries.",
        "title": "Insulin Prices to be Negotiated"
    },
    {
        "text": "Of the amounts authorized to be appropriated for the Department of Defense for fiscal year 2026, the Secretary of Defense shall allocate not less than $500,000,000 for the purposes of planning, developing, and sustaining cybersecurity infrastructure, including but not limited to network modernization, threat detection systems, and defensive cyber operations.",
        "topics": ["Defense", "Technology"],
        "tags": ["cybersecurity", "infrastructure funding"],
        "summary": "The Department of Defense allocates $500 million for cybersecurity infrastructure.",
        "title": "$500M allocated for cybersecurity"
    }
]"""

    # Generate the article using Claude
    user_message = f"Bill text to analyze:\n{bill.get('text')}\nResponse in a json structure with the following fields: text, topics, tags, summary, title"
    
    response = anthropic_client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    try:
        events = json.loads(response.content[0].text)

        print(f"Generated {len(events)} events")
        return events
    except:
        raise(Exception(f"Failed to generate valid json for bill {bill['bill_id']}"))


def process_event(bill, event):
    def _get_embedding(content):
        result = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=content,
        config=genai.types.EmbedContentConfig(output_dimensionality=768))

        [embedding_obj] = result.embeddings
        embedding_values_np = np.array(embedding_obj.values)
        normed_embedding = embedding_values_np / np.linalg.norm(embedding_values_np)

        return normed_embedding.tolist()

    content = ' '.join(event['topics']) + ' ' + ' '.join(event['tags']) + ' ' + event['summary']

    print('embedding content: ' + content)
    event['embedding'] = _get_embedding(content)

    actions = bill['actions']

    if actions and len(actions) > 0:
        latest = actions[-1]
        latest_action = latest.get('text', None)
    else:
        latest_action = None

    # Add bill data to event
    event['bill'] = {
        'id': bill['bill_id'],
        'title': bill['title'],
        'date': bill['latest_action_date'],
        'latest_action': latest_action
    }

    # add id and status to event
    event['id'] = bill['bill_id'] + '-' + str(uuid.uuid4())
    event['status'] = bill.get('status', 'pending')

    return event


def main(bill):
    events = get_events(bill)

    event_ids = []
    for event in events:
        event = process_event(bill, event)
        success = database.insert_event(events_collection, event)

        if success:
            print(f"Inserted event id {event['id']}")
        else:
            print(f"Failed to insert event id {event['id']}")

        event_ids.append(event['id'])
    
    # update bill
    bill['events'] = event_ids
    success = database.update_bill(bills_collection, bill)

    if success:
        print(f"Updated bill {bill['bill_id']} with events")
    else:
        print(f"Failed to update bill {bill['bill_id']} with events")


def handler(payload):
    id = payload.get("id")

    print(f"Processing event for bill: {id}")

    # Get bill from database
    bill = database.get_bill(bills_collection, id)

    main(bill)


if __name__ == "__main__":
    payload = {
        "id": "S2806-119",
        'type': 'new_bill'
    }
    id = payload.get("id")

    print(f"Processing event for bill: {id}")

    # Get bill from database
    bill = database.get_bill(bills_collection, id)

    main(bill)
