from pathlib import Path
from sentence_transformers import SentenceTransformer
import joblib as jb

BASE_DIR=Path(__file__).parent.resolve()

model=SentenceTransformer("all-MiniLM-L6-v2",cache_folder=f"{BASE_DIR}/vault_model_cache")

user_embed=model.encode(input("Enter your sentence : ")) #shape-(384,)

clf=jb.load(f"{BASE_DIR}/vault_model")

prediction=clf.predict(user_embed.reshape(1,384))
probability=clf.predict_proba(user_embed.reshape(1,384))

print(probability)
print(prediction)

