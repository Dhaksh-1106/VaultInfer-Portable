import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_VERBOSITY"] = "error"

import logging
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from pathlib import Path
from sentence_transformers import SentenceTransformer
import joblib as jb

BASE_DIR=Path(__file__).parent.resolve()

print("\nLoading Sentence Transfomer model...")
model=SentenceTransformer("all-MiniLM-L6-v2",cache_folder=f"{BASE_DIR}/vault_model_cache")

user_embed=model.encode(input("\nEnter your sentence : ")) #shape-(384,)

clf=jb.load(f"{BASE_DIR}/vault_model")

prediction=clf.predict(user_embed.reshape(1,384))
probability=clf.predict_proba(user_embed.reshape(1,384))

print("\n-------------ALERT---------------" if probability[0][1] > probability[0][0] else "\n-------------NORMAL--------------")
print(f"Probablity of Alert is : {probability[0][1]*100 : 0.2f} %\n")

