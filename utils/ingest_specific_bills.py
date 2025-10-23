from definitions.api import CongressGovAPI
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import sys
import common_utils.database as database
import common_utils.sqs as sqs
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY")
uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']

api = CongressGovAPI(API_KEY)

def main(bill_ids):
    """
    Process specified bill IDs instead of using CongressAPI search.
    
    Args:
        bill_ids: List of bill IDs in format like 'S1744-119', 'HR1716-119', etc.
    """
    logger.info(f"Processing {len(bill_ids)} specified bill IDs")

    updates = []
    revisions = []
    propogates = []
    seen = set()
    
    for bill_id_str in bill_ids:
        try:
            # Parse bill_id_str (e.g., 'S1744-119' -> type='S', number='1744', congress='119')
            parts = bill_id_str.split('-')
            if len(parts) != 2:
                logger.error(f"Invalid bill ID format: {bill_id_str}")
                continue
            
            bill_num_with_type = parts[0]
            congress = parts[1]
            
            # Extract bill type and number (e.g., 'S1744' -> 'S' and '1744')
            bill_type = ''.join([c for c in bill_num_with_type if c.isalpha()]).lower()
            bill_number = ''.join([c for c in bill_num_with_type if c.isdigit()])
            
            logger.info(f"Fetching bill: {bill_type}{bill_number} (Congress {congress})")
            
            # Fetch the specific bill from API
            bill = api.get_bill(congress=int(congress), bill_type=bill_type, bill_number=int(bill_number))
            
            if not bill:
                logger.warning(f"Could not fetch bill {bill_id_str}")
                continue
            
            # Not historical bills
            published_date = bill.get_published_date()
            if published_date and datetime.strptime(published_date, '%Y-%m-%d').year <= 2022:
                logger.debug(f"Skipping historical bill from {published_date}")
                continue
                
            # Check if bill is already in database
            bill_id = bill.get_id()

            if bill_id in seen:
                logger.debug(f"Bill {bill_id} already processed in this batch")
                continue

            existing_bill = database.get_bill(bills_collection, bill_id)

            logger.info(f"Processing bill {bill_id}: {bill.get_title()[:100]}...")
            logger.debug(f"  Latest Action Date: {bill.get_latest_action_date()}")

            # Skip bills with no text
            if bill.get_text_count() == 0:
                logger.info(f"  Skipping {bill_id} - no text available (text_count=0)")
                continue

            # Convert bill to dictionary with all information
            bill_data = bill.to_dict(text=True)
            new_text_length = len(bill_data.get('text', ''))
            logger.debug(f"  Fetched bill text: {new_text_length} characters")

            subjects = bill.get_subjects()
            logger.debug(f"  Subjects: {subjects}")

            if existing_bill:
                # Bill exists - determine what type of update is needed
                logger.info(f"  Bill {bill_id} exists in database - checking for changes")
                
                existing_text_length = len(existing_bill.get('text', ''))
                existing_action_date = existing_bill.get('latest_action_date', '')
                new_action_date = bill_data.get('latest_action_date', '')
                
                logger.debug(f"  Existing text length: {existing_text_length}, New text length: {new_text_length}")
                logger.debug(f"  Existing action date: {existing_action_date}, New action date: {new_action_date}")
                
                # Determine change type BEFORE updating
                change_detected = False
                
                # First time seeing this bill's text
                if existing_text_length == 0 and new_text_length > 0:
                    logger.info(f"  ✓ NEW TEXT detected for {bill_id} ({new_text_length} chars)")
                    updates.append(bill_id)
                    change_detected = True
                # Significant revision has been made (text length changed by >1000 chars)
                elif existing_text_length > 0 and abs(existing_text_length - new_text_length) > 1000:
                    text_diff = new_text_length - existing_text_length
                    logger.info(f"  ✓ REVISION detected for {bill_id} (text changed by {text_diff:+d} chars)")
                    revisions.append(bill_id)
                    change_detected = True
                # Action date changed but no significant text change
                elif existing_action_date != new_action_date:
                    logger.info(f"  ✓ PROPAGATION detected for {bill_id} (action date: {existing_action_date} → {new_action_date})")
                    propogates.append({
                        'bill_id': bill_id, 
                        'latest_action': bill.get_latest_action(), 
                        'date': new_action_date, 
                        'status': bill_data.get('status', '')
                    })
                    change_detected = True
                else:
                    logger.debug(f"  No significant changes detected for {bill_id}")
                
                # Now update the bill in database
                success = database.update_bill(bills_collection, bill_data)
                
                if success:
                    logger.debug(f"  Database updated successfully for {bill_id}")
                elif not change_detected:
                    logger.debug(f"  No database changes needed for {bill_id}")
                else:
                    logger.warning(f"  Database update returned no changes for {bill_id}")
                    
            else:
                # Bill doesn't exist - insert as new
                logger.info(f"  Bill {bill_id} is NEW - inserting into database")
                logger.debug(f"  Text length: {new_text_length}, Action date: {bill_data.get('latest_action_date', '')}")
                
                success = database.insert_bill(bills_collection, bill_data)
                
                if success:
                    logger.info(f"  ✓ NEW BILL inserted: {bill_id}")
                    updates.append(bill_id)
                else:
                    logger.error(f"  Failed to insert new bill {bill_id}")
            
            seen.add(bill_id)

        except Exception as e:
            logger.error(f"Error processing bill {bill_id_str}: {e}", exc_info=True)

    logger.info(f"="*60)
    logger.info(f"SUMMARY: Processed {len(seen)} bills")
    logger.info(f"  - New bills/text added: {len(updates)}")
    logger.info(f"  - Significant revisions: {len(revisions)}")
    logger.info(f"  - Propagations (action updates): {len(propogates)}")
    logger.info(f"="*60)
    
    if updates:
        logger.info(f"New bill IDs: {updates}")
    if revisions:
        logger.info(f"Revised bill IDs: {revisions}")
    if propogates:
        logger.info(f"Propagated bill IDs: {[p['bill_id'] for p in propogates]}")

    return updates, revisions, propogates

if __name__ == "__main__":
    bill_ids = [
        'S1744-119', 'HR1716-119', 'HR4860-119', 'HR5013-119', 'HR4233-119', 
        'HR1122-119', 'HR881-119', 'S321-119', 'HR2635-119', 'HR4830-119', 
        'HR4829-119', 'S2525-119', 'HR733-119', 'HR386-119', 'HR692-119', 
        'S1053-119', 'HR2246-119', 'HR2115-119', 'S680-119', 'HR1504-119', 
        'HR747-119', 'S2657-119', 'S1011-119'
    ]
    
    updates, revisions, propogates = main(bill_ids)
