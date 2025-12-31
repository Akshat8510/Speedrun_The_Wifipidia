# src/ai_logic.py
from sentence_transformers import SentenceTransformer, util

GLOBAL_HUBS = {
    "india", "united states", "science", "mathematics", "history", 
    "education", "university", "technology", "earth", "asia", "europe", "africa"
}

def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_score(link_title, target_title, link_vector, target_vector, keyword_bonus=0.25, hub_bonus=0.4):
    score = util.cos_sim(link_vector, target_vector).item()
    
    t_words = set(target_title.lower().split())
    l_words = set(link_title.lower().split())
    stop_words = {'the', 'of', 'in', 'and', 'a', 'to', 'for', 'is', 'on', 'disambiguation', 'institute'}
    
    clean_target = t_words - stop_words
    clean_link = l_words - stop_words
    
    # Keyword Stacking
    overlap = clean_target.intersection(clean_link)
    if overlap:
        score += (len(overlap) * keyword_bonus)

    # Hub Strategy
    if link_title.lower() in GLOBAL_HUBS:
        if len(overlap) == 0 and score < 0.5:
            score += hub_bonus
            
    return score 