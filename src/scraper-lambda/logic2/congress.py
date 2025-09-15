
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import re
import datetime
import time
import random

# NOTES
# - add cosponsors to people section
# - create workflow to requery text endpoint for bills missing text (may not be immeadiately available) in the case that it does not reappear in /bills endpoint


# Constants
DEFAULT_ARTICLE_AGE = 7
MAX_RETRIES = 10
BASE_DELAY = 0.33
MAX_DELAY = 15


class CongressGovAPI:
    BASE_URL = "https://api.congress.gov/v3"

    def __init__(self, api_key):
        self.api_key = api_key

    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        print(f"Query to: https://www.congress.gov/{endpoint}")
        params["api_key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    def get_bills(self, congress=None, bill_type=None, date_since_days=None):
        endpoint = "bill"
        params = {}
        if congress:
            endpoint += f"/{congress}"
        if bill_type:
            endpoint += f"/{bill_type}"

        if date_since_days is not None:
            # Calculate the date N days ago
            date_n_days_ago = datetime.date.today() - datetime.timedelta(days=date_since_days)
            params["fromDateTime"] = date_n_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        params["limit"] = 5  # Maximum limit

        data = self._make_request(endpoint, params=params)
        bills_data = data.get("bills", [])
        bill_objects = []
        for bill_summary in bills_data:
            congress_num = bill_summary.get("congress")
            bill_type = bill_summary.get("type")
            bill_number = bill_summary.get("number")

            if congress_num and bill_type and bill_number:
                bill_details = self.get_bill_details(congress_num, bill_type, bill_number)
                bill_objects.append(Bill(self, bill_details['bill']))
            else:
                # Fallback if summary doesn't have full details, try parsing billUri
                bill_uri = bill_summary.get("billUri")
                if bill_uri:
                    parts = bill_uri.split("/")
                    if len(parts) >= 6 and parts[-4] == "bill":
                        congress_num = int(parts[-3])
                        bill_type = parts[-2]
                        bill_number = int(parts[-1])
                        bill_details = self.get_bill_details(congress_num, bill_type, bill_number)
                        bill_objects.append(Bill(self, bill_details['bill']))
        return bill_objects

    def get_bill_details(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}"
        return self._make_request(endpoint)

    def get_bill_actions(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/actions"
        return self._make_request(endpoint).get("actions", [])

    def get_bill_amendments(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/amendments"
        return self._make_request(endpoint).get("amendments", [])

    def get_bill_committees(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/committees"
        return self._make_request(endpoint).get("committees", [])

    def get_bill_related_bills(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/relatedbills"
        return self._make_request(endpoint).get("relatedBills", [])

    def get_bill_subjects(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/subjects"
        return self._make_request(endpoint).get("subjects", [])

    def get_bill_summaries(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/summaries"
        return self._make_request(endpoint).get("summaries", [])

    def get_bill_text(self, congress, bill_type, bill_number):
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/text"
        return self._make_request(endpoint).get("textVersions", [])

    # Scraping utilities
    def get_document_text(self, url):
        try:
            response = self.fetch_with_retry(requests.get, url)
            
            if response.status_code == 200:
                # For PDF content
                if 'pdf' in url:
                    text = self._extract_text_from_pdf(response.content)
                else:
                    text = self._extract_text_from_html(response.text)
                
                # Clean the extracted text
                return self._clean_text(text)
            else:
                raise Exception(f"Failed to retrieve document: {response.status_code}")
                
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return f"Error retrieving document: {e}"


    def _extract_text_from_html(self, html_content):
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            
            # Get text content
            text = soup.get_text()

            # Get links
            links = soup.find_all('a')

            for link in links:
                link = link.get('href')
                if 'pdf' in link:
                    try:
                        response = requests.get(link)
                        if response.status_code == 200:
                            text += f"\n{self._extract_text_from_pdf(response.content)}"
                        else:
                            print(f"Failed to retrieve linked document: {response.status_code}")
                    except Exception as e:
                        print(f"Error retrieving linked document: {e}")

            
            # Clean up text: break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error extracting text from HTML: {e}")
            return html_content  # Return original content as fallback
    
    def _extract_text_from_pdf(self, pdf_content):
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                print("PDF is encrypted, cannot extract text")
                return "PDF is encrypted, cannot extract text"
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return "Error extracting text from PDF"

    def _clean_text(self, text):
        """
        Clean extracted text by removing extra spaces, normalizing whitespace,
        handling special characters, and improving readability.
        """
        if not text:
            return ""
            
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenation
        text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Fix decimal numbers
        
        # Replace special characters that might be incorrectly encoded
        text = text.replace('â€™', "'")
        text = text.replace('â€œ', '"')
        text = text.replace('â€', '"')
        text = text.replace('â€"', '-')
        text = text.replace('â€"', '--')
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Trim leading/trailing whitespace
        text = text.strip()
        
        return text

    def fetch_with_retry(self, func, *args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                time.sleep(min(BASE_DELAY * 2 ** attempt + random.uniform(0, 1), MAX_DELAY))

class Document:
    def __init__(self, api_client, data):
        self.api_client = api_client
        self.data = data

class Bill(Document):
    def __init__(self, api_client, data):
        super().__init__(api_client, data)
        self.congress = data["congress"]
        self.bill_type = data["type"].lower()
        self.bill_number = data["number"]
        self.bill_id = f"{data["type"]}{data["number"]}-{data["congress"]}"

    def get_id(self):
        return self.bill_id

    def get_title(self):
        return self.data.get("title")

    def get_latest_action_date(self):
        return self.data.get("latestAction", {}).get("actionDate")

    def get_actions(self):
        if isinstance(self.data.get("actions"), dict) and "count" in self.data.get("actions", {}):
            self.data["actions"] = self.api_client.get_bill_actions(self.congress, self.bill_type, self.bill_number)

            actions = []
            for action in self.data["actions"]:
                new_action = {
                    "date": action.get("actionDate"),
                    "text": action.get("text")
                }
                actions.append(new_action)

            self.data["actions"] = actions

        else:
            self.data["actions"] = self.data.get("actions", [])
        return self.data["actions"]

    def get_latest_action(self):
        if not isinstance(self.data.get("actions"), list):
            actions = self.get_actions()
        else:
            actions = self.data.get("actions", [])
        
        if actions and len(actions) > 0:
            return actions[-1]
        else:
            return None

    def get_amendments(self):
        if isinstance(self.data.get("amendments"), dict) and "count" in self.data.get("amendments", {}):
            self.data["amendments"] = self.api_client.get_bill_amendments(self.congress, self.bill_type, self.bill_number)
        
            amendments = []
            for amendment in self.data["amendments"]:
                amendments.append(Amendment(self.api_client, amendment))

            self.data["amendments"] = amendments
            return self.data["amendments"]
        return []

    def get_committees(self):
        if isinstance(self.data.get("committees"), dict) and "count" in self.data.get("committees", {}):
            self.data["committees"] = self.api_client.get_bill_committees(self.congress, self.bill_type, self.bill_number)
        
            committees = []
            for committee in self.data["committees"]:
                new_committee = {
                    "name": committee.get("name"),
                    "code": committee.get("systemCode"),
                    "chamber": committee.get("chamber")
                }
                committees.append(new_committee)
            
            self.data["committees"] = committees
            return self.data["committees"]
        return []

    def get_subjects(self):
        subjects = []
        if isinstance(self.data.get("subjects"), dict) and "count" in self.data.get("subjects", {}):
            self.data["subjects"] = self.api_client.get_bill_subjects(self.congress, self.bill_type, self.bill_number)

            if len(self.data["subjects"]["legislativeSubjects"]) > 0:
                subjects = [subj.get("name", "") for subj in self.data["subjects"]["legislativeSubjects"]]
            if self.data["subjects"]["policyArea"]:
                subjects.append(self.data["subjects"]["policyArea"])
        
        self.data["subjects"] = subjects
        return self.data["subjects"]

    def get_summary(self):
        self.data["summary"] = ""
        if isinstance(self.data.get("summaries"), dict) and "count" in self.data.get("summaries", {}):
            self.data["summaries"] = self.api_client.get_bill_summaries(self.congress, self.bill_type, self.bill_number)
        
            if len(self.data["summaries"]) > 0:
                self.data["summary"] = self.data["summaries"][-1].get("text", "")
        
        return self.data["summary"]

    def get_text(self):
        if 'text' not in self.data:
            self.data["textVersions"] = self.api_client.get_bill_text(self.congress, self.bill_type, self.bill_number)

            if isinstance(self.data["textVersions"], list) and len(self.data["textVersions"]) > 0:
                recent = self.data["textVersions"][-1]

                text = ""
                for format in recent.get("formats", []):
                    url = format.get('url')
                    if format.get("type") == "Formatted Text" or format.get("type") == "PDF":
                        print(f"URL: {url}")

                        try:
                            text = self.api_client.get_document_text(url)
                            break  # Exit after successfully processing the first valid URL
                        except Exception as e:
                            print(f"Error fetching document text from {url}: {e}")
                
                self.data["text"] = text
            else:
                self.data["text"] = ""

        return self.data["text"]
    
    def get_sponsors(self):
        if 'sponsors' in self.data and 'people' not in self.data:
            sponsors = []
            for sponsor in self.data['sponsors']:
                new_sponsor = {
                    "name": sponsor.get("fullName"),
                    "state": sponsor.get("state"),
                    "party": sponsor.get("party"),
                    "district": sponsor.get("district"),
                    "bioguideId": sponsor.get("bioguideId"),
                }
                sponsors.append(new_sponsor)
            self.data['people'] = sponsors

        if 'people' in self.data:
            return self.data['people']
        return []

    def get_details(self):
        self.get_actions()
        self.get_summary()
        self.get_amendments()
        self.get_committees()

        self.data["full"] = True

    def to_dict(self):
        """
        Return a dictionary object with only the essential attributes of the bill.
        """

        if "full" not in self.data or not self.data["full"]:
            self.get_details()

        bill = {
            "title": self.data.get("title"),
            "text": self.data.get("text") if "text" in self.data else self.get_text(),
            "congress": self.congress,
            "bill_type": self.bill_type,
            "bill_number": self.bill_number,
            "bill_id": self.bill_id,
            "subjects": self.data.get("subjects", ""),
            "latest_action_date": self.get_latest_action_date() if self.get_latest_action_date() else self.data.get("introducedDate"),
            "published_date": self.data.get("introducedDate"),
            'actions': self.data.get("actions", []),
            'summary': self.data.get("summary", ""),
            'amendments': [amendment.data for amendment in self.data.get("amendments", [])],
            'committees': self.data.get("committees", []),
            'people': self.get_sponsors(),
            'url': f'https://www.congress.gov/bill/{self.congress}/{self.bill_type}/{self.bill_number}',
        }

        return bill





class Amendment(Document):
    def __init__(self, api_client, data):
        super().__init__(api_client, data)
        self.congress = data["congress"]
        self.amendment_type = data["type"]
        self.amendment_number = data["number"]

    def get_id(self):
        return self.data.get("amendmentId")

    def get_title(self):
        return self.data.get("title")

    def get_latest_action_date(self):
        return self.data.get("latestAction", {}).get("actionDate")

    def get_actions(self):
        endpoint = f"amendment/{self.congress}/{self.amendment_type}/{self.amendment_number}/actions"
        return self.api_client._make_request(endpoint).get("actions", [])

    def get_cosponsors(self):
        endpoint = f"amendment/{self.congress}/{self.amendment_type}/{self.amendment_number}/cosponsors"
        return self.api_client._make_request(endpoint).get("cosponsors", [])

    def get_amendments(self):
        endpoint = f"amendment/{self.congress}/{self.amendment_type}/{self.amendment_number}/amendments"
        return self.api_client._make_request(endpoint).get("amendments", [])

    def get_text_versions(self):
        endpoint = f"amendment/{self.congress}/{self.amendment_type}/{self.amendment_number}/text"
        return self.api_client._make_request(endpoint).get("textVersions", [])


class Law(Document):
    def __init__(self, api_client, data):
        super().__init__(api_client, data)
        self.congress = data["congress"]
        self.law_type = data["type"]
        self.law_number = data["number"]

    def get_id(self):
        return self.data.get("lawId")

    def get_title(self):
        return self.data.get("title")

    def get_latest_action_date(self):
        return self.data.get("enactedDate") # Laws have an enactedDate instead of latestAction

    def get_text_versions(self):
        endpoint = f"law/{self.congress}/{self.law_type}/{self.law_number}/text"
        return self.api_client._make_request(endpoint).get("textVersions", [])
