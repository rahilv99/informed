import os
import requests
import logging
import json
import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote_plus

# Set cache directories to writable location in Lambda BEFORE importing sentence_transformers
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['HF_HUB_CACHE'] = '/tmp/huggingface/hub'

from sentence_transformers import SentenceTransformer
from article_resource import ArticleResource #revert to logic.article_resource

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Congress Documents Integration
class Congress(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.fuzzy_threshold = 95
        self.api_key = os.environ.get('CONGRESS_API_KEY')
        self.headers = {"Content-Type": "application/json"}

        self.today = datetime.datetime.now()  # Current date
        self.time_constraint = datetime.datetime.now() - datetime.timedelta(days=7)  # 7 days ago
        
        # Initialize semantic similarity model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.2  # Minimum similarity score to include bill

    def get_bills(self):
        """
        Fetch recent bills from the Congress API and filter by semantic similarity to user interests.
        Only returns bills that are semantically similar to at least one interest above the threshold.
        
        Returns:
            list: List of dicts with bill info, filtered by semantic similarity to user interests
        """
        try:
            results = []
            seen_titles = set()
            
            # Build URL - get all recent bills without search query since API search is broken
            if self.time_constraint:
                from_date = self.time_constraint.strftime('%Y-%m-%dT%H:%M:%SZ')
                to_date = self.today.strftime('%Y-%m-%dT%H:%M:%SZ')
                url = (f"https://api.congress.gov/v3/bill/119?"
                       f"fromDateTime={from_date}"
                       f"&toDateTime={to_date}"
                       f"&api_key={self.api_key}")
            else:
                # Get all available bills without time constraints
                url = f"https://api.congress.gov/v3/bill/119?api_key={self.api_key}"

            try:
                print(f"Fetching bills from Congress API: {url}")
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    bills = data.get('bills', [])
                    print(f"Retrieved {len(bills)} bills from Congress API")

                    if not bills:
                        print("No bills found from Congress API")
                        return None

                    # Process all bills
                    all_bills = []
                    for bill in bills:
                        title = bill.get('title', '')

                        if title and self._is_duplicate_title(title, seen_titles):
                            print(f"Skipping duplicate bill: {title}")
                            continue
                        
                        if title:
                            seen_titles.add(title.lower().strip())

                        congress_num = bill.get('congress')
                        bill_type = bill.get('type', '').lower()
                        bill_number = bill.get('number')

                        bill_identifier = None
                        if congress_num and bill_type and bill_number:
                            # Example: "hr3876-119"
                            bill_identifier = f"{bill_type}{bill_number}-{congress_num}"
                        
                        # Get basic bill information
                        bill_url = bill.get('url', '')
                        latest_action = bill.get('latestAction', {})
                        latest_action_date = latest_action.get('actionDate', '')
                        latest_action_text = latest_action.get('text', '')
                        
                        all_bills.append({
                            "title": title,
                            "bill_id": bill_identifier,
                            "url": bill_url,
                            "latest_action_date": latest_action_date,
                            "latest_action_text": latest_action_text,
                            "congress": congress_num,
                            "bill_type": bill_type,
                            "bill_number": bill_number
                        })
                        
                    print(f"Processed {len(all_bills)} unique bills")
                    
                    # Apply semantic filtering against all user interests
                    if self.user_input and all_bills:
                        print(f"Applying semantic filtering against {len(self.user_input)} interests: {self.user_input}")
                        filtered_results = self._filter_bills_by_interests(all_bills, self.user_input)
                        print(f"Semantic filtering reduced results from {len(all_bills)} to {len(filtered_results)} bills")
                        results = filtered_results
                    else:
                        results = all_bills
                    
                    if results:
                        # Sort results by similarity score (highest first), then by latest action date
                        results.sort(key=lambda x: (x.get('similarity_score', 0), x.get('latest_action_date', '')), reverse=True)
                        print(f"Successfully retrieved {len(results)} bills.")
                        print("Top bills by similarity score:")
                        for i, bill in enumerate(results[:5]):  # Show top 5
                            similarity = bill.get('similarity_score', 'N/A')
                            keyword = bill.get('keyword', 'N/A')
                            print(f"  {i+1}. {bill['title'][:60]}... - Similarity: {similarity} (Keyword: {keyword})")
                        return results
                    else:
                        print("No bills found matching the search criteria.")
                        return None
                        
                else:
                    print(f"Congress API request failed. Status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as req_err:
                print(f"Network or request error: {req_err}")
                return None
            except json.JSONDecodeError as json_err:
                print(f"JSON decoding error: {json_err}. Response: {response.text}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred processing Congress API query: {e}")
                return None

        except Exception as e:
            print(f"Error in Congress integration's get_bills method: {e}")
            return None
    
    def _filter_bills_by_interests(self, bills, interests):
        """
        Filter bills by semantic similarity to any of the user interests.
        Only returns bills that are similar to at least one interest above the threshold.
        
        Args:
            bills (list): List of bill dictionaries
            interests (list): List of interest strings to compare against
            
        Returns:
            list: Filtered list of bills above similarity threshold for at least one interest
        """
        try:
            if not bills or not interests:
                return bills
                
            # Prepare texts for similarity comparison
            bill_texts = []
            for bill in bills:
                # Combine title and latest action text for better semantic matching
                text = f"{bill.get('title', '')} {bill.get('latest_action_text', '')}"
                bill_texts.append(text)
            
            # Encode all interests and bill texts
            interest_embeddings = self.model.encode(interests)
            bill_embeddings = self.model.encode(bill_texts)
            
            # Calculate cosine similarities between each bill and all interests
            similarities_matrix = cosine_similarity(bill_embeddings, interest_embeddings)
            
            # Filter bills that match at least one interest above threshold
            filtered_bills = []
            for i, (bill, bill_similarities) in enumerate(zip(bills, similarities_matrix)):
                # Find the best matching interest for this bill
                max_similarity_idx = np.argmax(bill_similarities)
                max_similarity = bill_similarities[max_similarity_idx]
                best_interest = interests[max_similarity_idx]
                
                if max_similarity >= self.similarity_threshold:
                    bill_copy = bill.copy()
                    bill_copy['similarity_score'] = float(max_similarity)
                    bill_copy['keyword'] = best_interest  # Add the best matching interest as keyword
                    filtered_bills.append(bill_copy)
                    print(f"  Bill '{bill['title'][:60]}...' - Similarity: {max_similarity:.3f} (Interest: '{best_interest}')")
            
            return filtered_bills
            
        except Exception as e:
            print(f"Error in semantic filtering by interests: {e}")
            return bills  # Return original bills if filtering fails
    
    def _filter_bills_by_similarity(self, bills, query):
        """
        Filter bills by semantic similarity to the query using sentence transformers.
        
        Args:
            bills (list): List of bill dictionaries
            query (str): Query string to compare against
            
        Returns:
            list: Filtered list of bills above similarity threshold
        """
        try:
            if not bills or not query:
                return bills
                
            # Prepare texts for similarity comparison
            bill_texts = []
            for bill in bills:
                # Combine title and latest action text for better semantic matching
                text = f"{bill.get('title', '')} {bill.get('latest_action_text', '')}"
                bill_texts.append(text)
            
            # Encode query and bill texts
            query_embedding = self.model.encode([query])
            bill_embeddings = self.model.encode(bill_texts)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, bill_embeddings)[0]
            
            # Filter bills above threshold and add similarity scores
            filtered_bills = []
            for i, (bill, similarity) in enumerate(zip(bills, similarities)):
                if similarity >= self.similarity_threshold:
                    bill_copy = bill.copy()
                    bill_copy['similarity_score'] = float(similarity)
                    bill_copy['keyword'] = query  # Add the query as keyword for compatibility
                    filtered_bills.append(bill_copy)
                    print(f"  Bill '{bill['title'][:60]}...' - Similarity: {similarity:.3f}")
            
            # Sort by similarity score (highest first)
            filtered_bills.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return filtered_bills
            
        except Exception as e:
            print(f"Error in semantic filtering: {e}")
            return bills  # Return original bills if filtering fails
            
def handler(payload):
    """
    AWS Lambda handler function to process incoming events for Congress bills.
    """
    topics = payload.get("topics")
    if not topics:
        print("No topics provided in the payload.")
        return {"statusCode": 400, "body": "Missing 'topics' in payload."}

    print(f"congress_scraper invoked with topics: {topics}")
    congress = Congress(topics)
    bills = congress.get_bills()

    if bills is not None and len(bills) > 0:
        print(f"Retrieved {len(bills)} bills.")
        for entry in bills:
            print(f"Title: {entry['title']}")
            print(f"Bill ID: {entry['bill_id']}") 
            print(f"URL: {entry['url']}")
            print(f"Keyword: {entry['keyword']}")
            print(f"Latest Action Date: {entry['latest_action_date']}")
            print(f"Latest Action Text: {entry['latest_action_text']}")
            print("--------------------")
        return {"statusCode": 200, "body": json.dumps(bills)}
    else:
        print("No bills found.")
        return {"statusCode": 204, "body": "No bills found."}

if __name__ == "__main__":
    if os.environ.get('CONGRESS_API_KEY'):
        keywords = ["Trade", "Energy","Cybersecurity","Technology", "Economics", "Voting", "International Relations"] 
        
        # Test get_bills() method directly
        print("--- Testing get_bills() method directly ---")
        congress = Congress(keywords)
        bills_result = congress.get_bills()
        print("get_bills() returned:")
        print(bills_result)
        
        # Test handler function
        payload = {"topics": keywords}
        print("\n--- Invoking handler with example keywords ---")
        handler(payload)
    else:
        print("CONGRESS_API_KEY environment variable not set. Please set it to run the example.")
