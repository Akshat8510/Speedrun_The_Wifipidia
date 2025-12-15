import streamlit as st
import heapq
import time
import wikipediaapi
from sentence_transformers import SentenceTransformer, util

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wiki Speedrun AI", page_icon="🧠", layout="centered")

# --- 1. CONFIGURATION ---
BEAM_WIDTH = 4        # Increased to explore more options
MAX_STEPS = 50
UNIQUE_WORD_BONUS = 0.2  # Bonus per matching word
HUB_BONUS = 0.4          # Bonus for finding a Hub

# Global Hubs to escape traps
GLOBAL_HUBS = {
    "india", "united states", "science", "mathematics", "history", 
    "education", "university", "technology", "earth", "asia", "europe", "africa",
    "list of universities in india", "states and union territories of india"
}

# --- 2. CACHED RESOURCES ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_wiki_agent():
    return wikipediaapi.Wikipedia(
        user_agent='StreamlitWikiBot/3.0 (educational)',
        language='en'
    )

try:
    model = load_model()
    wiki = get_wiki_agent()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

# --- 3. CORE FUNCTIONS ---

def get_valid_links(page_obj):
    links = []
    try:
        if not page_obj.exists(): return []
        for title in page_obj.links.keys():
            if ":" not in title:
                links.append(title)
    except:
        pass
    return links

def resolve_redirect(title):
    page = wiki.page(title)
    if page.exists():
        return page.title
    return title

def calculate_score(link_title, target_title, link_vector, target_vector):
    """
    Advanced Scoring: 
    Vector Similarity + Word Overlap Count + Hub Bonus
    """
    # 1. Vector Similarity
    score = util.cos_sim(link_vector, target_vector).item()
    
    # 2. Keyword Stacking (The Fix for "Institute" loops)
    t_words = set(target_title.lower().split())
    l_words = set(link_title.lower().split())
    
    # Remove generic words that cause confusion
    stop_words = {
        'the', 'of', 'in', 'and', 'a', 'to', 'for', 'is', 'on', 
        'disambiguation', 'institute', 'university', 'college', 'technology', 'engineering'
    }
    
    clean_target = t_words - stop_words
    clean_link = l_words - stop_words
    
    # Calculate overlap count
    overlap = clean_target.intersection(clean_link)
    
    # Add bonus for EACH unique matching word (e.g. "Kalinga", "Odisha")
    if overlap:
        score += (len(overlap) * UNIQUE_WORD_BONUS)

    # 3. Hub Strategy
    if link_title.lower() in GLOBAL_HUBS:
        # Only use hub if we aren't finding direct keyword matches
        if len(overlap) == 0 and score < 0.5:
            score += HUB_BONUS
            
    return score

# --- 4. UI LAYOUT ---
st.title("🧠 AI Wikipedia Speedrunner")
st.caption("Now with Weighted Keyword Scoring to avoid 'Category Traps'")

col1, col2 = st.columns(2)
with col1:
    start_input = st.text_input("Start Page", value="Achyuta")
with col2:
    target_input = st.text_input("Target Page", value="Kalinga Institute of Industrial Technology")

start_btn = st.button("🚀 Start Speedrun", type="primary")

# --- 5. EXECUTION LOGIC ---
if start_btn:
    if not start_input or not target_input:
        st.warning("Please enter both pages.")
        st.stop()

    status_container = st.container()
    
    with status_container:
        st.info("Initializing...")
        start_title = resolve_redirect(start_input)
        target_title = resolve_redirect(target_input)
        
        target_embedding = model.encode(target_title, convert_to_tensor=True)
        
        queue = [(-0.0, [start_title])]
        visited = set([start_title])
        steps = 0
        
        progress_bar = st.progress(0)
        current_step_text = st.empty()
        log_expander = st.expander("View AI Reasoning", expanded=True)
        
        start_time = time.time()
        success = False
        final_path = []

        while queue and steps < MAX_STEPS:
            steps += 1
            progress_bar.progress(min(steps * 2, 100))
            
            # Pop best path
            score, path = heapq.heappop(queue)
            current_title = path[-1]
            
            current_step_text.markdown(f"**Step {steps}:** Visiting `{current_title}` (Score: {-score:.2f})")
            
            with log_expander:
                st.write(f"📍 **{current_title}**")

            # WIN CHECKS
            if current_title.lower() == target_title.lower():
                success = True; final_path = path; break
            
            # Substring check for long university names
            if target_title.lower() in current_title.lower() and len(current_title) < len(target_title) + 10:
                 success = True; final_path = path; break

            # Get Links
            current_page = wiki.page(current_title)
            links = get_valid_links(current_page)
            
            if not links: continue
                
            # Quick Win
            matches = [l for l in links if l.lower() == target_title.lower()]
            if matches:
                path.append(matches[0])
                success = True; final_path = path; break
            
            # AI Processing
            # Scan top 200 links to ensure we don't miss "Odisha"
            links_to_scan = links[:200] if len(links) > 200 else links
            link_vectors = model.encode(links_to_scan, convert_to_tensor=True, show_progress_bar=False)
            
            scored_links = []
            for i, link in enumerate(links_to_scan):
                s = calculate_score(link, target_title, link_vectors[i], target_embedding)
                scored_links.append((s, link))
                
            scored_links.sort(key=lambda x: x[0], reverse=True)
            
            # Logging top choices
            with log_expander:
                top_choices = [f"{l} ({s:.2f})" for s, l in scored_links[:3]]
                st.caption(f"Next best: {', '.join(top_choices)}")

            # Beam Search
            added = 0
            for s, link in scored_links:
                if link not in visited:
                    visited.add(link)
                    new_path = list(path)
                    new_path.append(link)
                    heapq.heappush(queue, (-s, new_path))
                    added += 1
                    if added >= BEAM_WIDTH:
                        break
        
        end_time = time.time()

        # --- FINAL OUTPUT ---
        if success:
            st.balloons()
            st.success(f"🏆 TARGET REACHED in {end_time - start_time:.2f} seconds!")
            
            path_str = ""
            for i, p in enumerate(final_path):
                link = f"https://en.wikipedia.org/wiki/{p.replace(' ', '_')}"
                if i < len(final_path) - 1:
                    path_str += f"[{p}]({link}) ➡️ "
                else:
                    path_str += f"**[{p}]({link})**"
            
            st.markdown(path_str)
            st.markdown(f"**Total Clicks:** {len(final_path) - 1}")
        else:
            st.error("💀 The AI got lost.")
