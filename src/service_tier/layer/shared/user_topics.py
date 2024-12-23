from sentence_transformers import SentenceTransformer, util
import pickle

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and effective model

DEFATULT_TOP_TAXONOMY_MATCHES = 3  # Number of top matches to consider for each keyword

# TODO This should be done only once at initialization 
with open('./data/candidate_words.pkl', 'rb') as file:
    candidate_words = pickle.load(file)

class UserTopics:
    def __init__(self, user_input=['Generative AI','Data Engineering','Large Language Models','Speech Synthesis']): # Hardcoded for now
        user_input = [x.lower() for x in user_input]
        self.user_input = user_input
        self.expanded_input = []
        self.all_input = []
        self._expand_input_sbert()
        self.expanded_embeddings
        self.user_input_embeddings 

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