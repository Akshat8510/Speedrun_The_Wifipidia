import streamlit as st
import heapq
import time
import wikipediaapi
from sentence_transformers import SentenceTransformer, util

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wiki Speedrun AI", page_icon="🧠", layout="centered")

# --- 1. CONFIGURATION & CONSTANTS ---
BEAM_WIDTH = 3
MAX_STEPS = 50
KEYWORD_BONUS = 0.25

# THE HUB STRATEGY: 
# If the AI gets confused (low score), it will prioritize these pages to reset its path.
GLOBAL_HUBS = {
    "india", "united states", "science", "mathematics", "history", 
    "education", "university", "technology", "earth", "asia", "europe", "africa"
}

# --- 2. CACHED RESOURCE LOADING ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_wiki_agent():
    # Randomize user agent slightly to prevent shared-IP blocking
    return wikipediaapi.Wikipedia(
        user_agent='StreamlitWikiBot/2.0 (educational)',
        language='en'
    )

# Load resources immediately
try:
    model = load_model()
    wiki = get_wiki_agent()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

# --- 3. HELPER FUNCTIONS ---

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
    Calculates the priority score for a link.
    Logic: Vector Similarity + Keyword Match + Hub Bonus
    """
    # 1. Base Semantic Score (Vector Math)
    vec_score = util.cos_sim(link_vector, target_vector).item()
    
    # 2. Keyword Bonus
    t_words = set(target_title.lower().split())
    l_words = set(link_title.lower().split())
    stop_words = {'the', 'of', 'in', 'and', 'a', 'to', 'for', 'is', 'on', 'disambiguation', 'university', 'institute'}
    
    clean_target = t_words - stop_words
    clean_link = l_words - stop_words
    
    score = vec_score
    
    # If words overlap, give a bonus
    if not clean_target.isdisjoint(clean_link):
        score += KEYWORD_BONUS

    # 3. THE HUB STRATEGY (Panic Button)
    # If the vector score is low (AI is confused), boost Hub pages to find a way out.
    if link_title.lower() in GLOBAL_HUBS:
        # Only apply hub bonus if we aren't already finding good matches (score < 0.4)
        if vec_score < 0.4: 
            score += 0.3  # Massive boost to force a reset to a main page
            
    return score

# --- 4. UI LAYOUT ---
st.title("🧠 AI Wikipedia Speedrunner")
st.markdown("Watch an AI navigate from point A to point B using Semantic Vector Search.")

col1, col2 = st.columns(2)
with col1:
    start_input = st.text_input("Start Page", value="Achyuta")
with col2:
    target_input = st.text_input("Target Page", value="Kalinga Institute of Industrial Technology")

start_btn = st.button("🚀 Start Speedrun", type="primary")

# --- 5. RUNNER LOGIC ---
if start_btn:
    if not start_input or not target_input:
        st.warning("Please enter both pages.")
        st.stop()

    status_container = st.container()
    
    with status_container:
        st.info("Resolving titles and initializing AI...")
        start_title = resolve_redirect(start_input)
        target_title = resolve_redirect(target_input)
        
        target_embedding = model.encode(target_title, convert_to_tensor=True)
        
        # Priority Queue: (-Score, [Path])
        queue = [(-0.0, [start_title])]
        visited = set([start_title])
        steps = 0
        
        # UI Elements for live updates
        progress_bar = st.progress(0)
        current_step_text = st.empty()
        log_expander = st.expander("View AI Thinking Process", expanded=True)
        
        start_time = time.time()
        success = False
        final_path = []

        while queue and steps < MAX_STEPS:
            steps += 1
            progress_bar.progress(min(steps * 2, 100))
            
            # Get best option
            score, path = heapq.heappop(queue)
            current_title = path[-1]
            
            current_step_text.markdown(f"**Step {steps}:** Visiting `{current_title}` (Score: {-score:.2f})")
            
            # Update Logs
            with log_expander:
                st.write(f"📍 At: **{current_title}**")

            # WIN CONDITION
            if current_title.lower() == target_title.lower() or \
               (target_title.lower() in current_title.lower() and "disambiguation" in current_title.lower()):
                success = True
                final_path = path
                break
            
            # Fetch Links
            current_page = wiki.page(current_title)
            links = get_valid_links(current_page)
            
            if not links: continue
                
            # Quick Win Check
            matches = [l for l in links if l.lower() == target_title.lower()]
            if matches:
                path.append(matches[0])
                success = True
                final_path = path
                break
            
            # AI Processing
            # Limit links to scan to keep speed high
            links_to_scan = links[:150] if len(links) > 150 else links
            link_vectors = model.encode(links_to_scan, convert_to_tensor=True, show_progress_bar=False)
            
            scored_links = []
            for i, link in enumerate(links_to_scan):
                s = calculate_score(link, target_title, link_vectors[i], target_embedding)
                scored_links.append((s, link))
                
            scored_links.sort(key=lambda x: x[0], reverse=True)
            
            # Show top 3 choices in logs for user to see
            with log_expander:
                top_choices = [f"{l} ({s:.2f})" for s, l in scored_links[:3]]
                st.caption(f"Top ideas: {', '.join(top_choices)}")

            # Beam Search: Add best options to queue
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

        # --- RESULTS ---
        if success:
            st.balloons()
            st.success(f"🏆 TARGET REACHED in {end_time - start_time:.2f} seconds!")
            st.markdown("### The Path:")
            
            path_str = ""
            for i, p in enumerate(final_path):
                if i < len(final_path) - 1:
                    path_str += f"[{p}](https://en.wikipedia.org/wiki/{p.replace(' ', '_')}) ➡️ "
                else:
                    path_str += f"**[{p}](https://en.wikipedia.org/wiki/{p.replace(' ', '_')})**"
            
            st.markdown(path_str)
            st.markdown(f"**Total Clicks:** {len(final_path) - 1}")
        else:
            st.error("💀 The AI got lost or ran out of steps. Try a Global Hub in the path!")
