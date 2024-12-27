from sentence_transformers import SentenceTransformer, util
import common.s3
import pickle

model = SentenceTransformer('./saved_model/all-MiniLM-L6-v2')  # Lightweight and effective model

DEFATULT_TOP_TAXONOMY_MATCHES = 3  # Number of top matches to consider for each keyword

# TODO This should be done only once at initialization 
with open('./research/data/candidate_words.pkl', 'rb') as file:
    candidate_words = pickle.load(file)

class UserTopics:
    def __init__(self, user_id, user_input): # Hardcoded for now
        user_input = [x.lower() for x in user_input]
        self.user_input = user_input
        self.expanded_input = []
        self.all_input = []
        self.expanded_embeddings = None
        self.user_input_embeddings = None
        self.user_id = user_id

        self._expand_input_sbert()


    def _expand_input_sbert(self):
        top_candidates = {}
        input_embeddings = model.encode(self.user_input, convert_to_tensor=True)
        candidate_embeddings = model.encode(candidate_words, convert_to_tensor=True)

        for i, keyword in enumerate(self.user_input):
            # Compute cosine similarity between the input and all candidates
            cosine_scores = util.cos_sim(input_embeddings[i], candidate_embeddings)
            cosine_scores = cosine_scores.cpu().numpy()[0]
            # sort descending
            cosine_scores = cosine_scores.argsort()[::-1]
            # Get the top N most similar words
            top_results = cosine_scores[:DEFATULT_TOP_TAXONOMY_MATCHES]
            top_candidates[keyword] = [candidate_words[idx] for idx in top_results]

        
        self.expanded_input = [item for sublist in top_candidates.values() for item in sublist]
        self.expanded_input = list(set(self.expanded_input))
        print(f'Expanded Input: {self.expanded_input}, User Input: {self.user_input}')
        self.expanded_embeddings = model.encode(" ".join(self.expanded_input), convert_to_tensor=True) # Will be needed later for scoring so do it only once
        self.user_input_embeddings = model.encode(" ".join(self.user_input), convert_to_tensor=True) 

        self.all_input = self.user_input + self.expanded_input

        # Save output to S3
        print('Trying to save output')
        common.s3.save_serialized(self.user_id, "USER_TOPICS", {
            "expanded_embeddings": self.expanded_embeddings,
            "user_input_embeddings": self.user_input_embeddings,
            "all_input": self.all_input
        })

# Main Execution
def handler(payload):
    user_input = payload.get("user_input")
    user_id = payload.get("user_id")
    if (user_input == None):
        print('User Topics: No input specified - using default')
        user_input = ['Generative AI','Data Engineering','Large Language Models','Speech Synthesis']
    print(f"User Input Is: {user_input}")
    try:
        user_topics = UserTopics(user_id, user_input)
    except Exception as e:
        print(f"Got Exception {e}")

if __name__ == "__main__":
    handler(None)