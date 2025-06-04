import clean
import merge
import dispatch
import json
import traceback
import legal_scraper

def _handler(event, context):
    """
    Main Lambda handler
    :param event: Input event with 'action' and 'payload'
    :param context: AWS Lambda context object
    """
     # Check if the event is triggered by SQS
    json_message = None
    if "Records" in event and event["Records"][0].get("eventSource") == "aws:sqs":
        print(f"Scraper Helper Lambda Invoked from SQS")

    for record in event["Records"]:
        json_message = json.loads(record["body"])

        # Extract the action and payload
        action = json_message.get('action')
        payload = json_message.get('payload', {})
        print(f"Scraper helper Lambda Invoked with action {action}")

        # Map actions to internal functions
        action_map = {
            "e_merge": merge.handler,
            "e_clean": clean.handler,
            "e_dispatch": dispatch.handler,
            "e_gov": legal_scraper.handler
        }

        # Route to the appropriate function
        if action in action_map:
            result = action_map[action](payload)
        else:
            print(f"Unsupported Action {action}")

def handler(event, context):
    try:
        _handler(event, context)
        return {
            "statusCode": 200,
            "body": "Success"
        }
    except Exception as e:
        print(f"Lambda Exception {e}")
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": f"Error executing action '{event}': {str(e)}"
        }