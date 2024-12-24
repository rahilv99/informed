import sys

from sentence_transformers import SentenceTransformer

# Load the pretrained model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
save_location = sys.argv[1] 

# Save the model locally
model.save(f'{save_location}/all-MiniLM-L6-v2')
print("Model saved locally.")
