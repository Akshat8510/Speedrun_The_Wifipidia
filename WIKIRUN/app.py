import streamlit as st
import heapq
import time
import wikipediaapi
from sentence_transformers import SentenceTransformer, util

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wiki Speedrun AI", page_icon="🧠", layout="centered")

# --- 1. CACHED RESOURCE LOADING (Crucial for Web App) ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_wiki_agent():
    # Randomize user agent slightly to prevent shared-IP blocking
    return wikipediaapi.Wikipedia(
        user_agent='StreamlitWikiBot/1.0 (educational)',
        language='en'
    )

# Load resources immediately
try:
    model = load_model()
    wiki = get_wiki_agent()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

# --- 2. CORE LOGIC ---
BEAM_WIDTH = 3
MAX_STEPS = 50
KEYWORD_BONUS = 0.25

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
    vec_score = util.cos_sim(link_vector, target_vector).item()
    
    t_words = set(target_title.lower().split())
    l_words = set(link_title.lower().split())
    stop_words = {'the', 'of', 'in', 'and', 'a', 'to', 'for', 'is', 'on', 'disambiguation'}
    
    clean_target = t_words - stop_words
    clean_link = l_words - stop_words
    
    if not clean_target.isdisjoint(clean_link):
        return vec_score + KEYWORD_BONUS
    
    return vec_score

# --- 3. UI LAYOUT ---
st.title("🧠 AI Wikipedia Speedrunner")
st.markdown("Watch an AI navigate from point A to point B using Semantic Vector Search.")

col1, col2 = st.columns(2)
with col1:
    start_input = st.text_input("Start Page", value="SpongeBob SquarePants")
with col2:
    target_input = st.text_input("Target Page", value="Nuclear Power")

start_btn = st.button("🚀 Start Speedrun", type="primary")

# --- 4. RUNNER LOGIC ---
if start_btn:
    if not start_input or not target_input:
        st.warning("Please enter both pages.")
        st.stop()

    status_container = st.container()
    
    with status_container:
        st.info("resolving titles...")
        start_title = resolve_redirect(start_input)
        target_title = resolve_redirect(target_input)
        
        target_embedding = model.encode(target_title, convert_to_tensor=True)
        
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
                
            # Quick Win
            matches = [l for l in links if l.lower() == target_title.lower()]
            if matches:
                path.append(matches[0])
                success = True
                final_path = path
                break
            
            # AI Processing
            links_to_scan = links[:120] if len(links) > 120 else links
            link_vectors = model.encode(links_to_scan, convert_to_tensor=True, show_progress_bar=False)
            
            scored_links = []
            for i, link in enumerate(links_to_scan):
                s = calculate_score(link, target_title, link_vectors[i], target_embedding)
                scored_links.append((s, link))
                
            scored_links.sort(key=lambda x: x[0], reverse=True)
            
            # Show top 3 choices in logs
            with log_expander:
                top_choices = [f"{l} ({s:.2f})" for s, l in scored_links[:3]]
                st.caption(f"Top ideas: {', '.join(top_choices)}")

            # Beam Add
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
            st.error("💀 The AI got lost or ran out of steps.")