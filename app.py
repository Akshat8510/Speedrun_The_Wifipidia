import streamlit as st
import heapq
import time
import os

# Import our new modules
from src import scraper, ai_logic, database, visualizer

# Initialize App
st.set_page_config(page_title="Wiki Speedrun Pro", page_icon="🧠", layout="centered")
database.init_db() # Ensure DB exists

# --- LOAD RESOURCES ---
@st.cache_resource
def load_resources():
    model = ai_logic.load_model()
    wiki = scraper.get_wiki_agent()
    return model, wiki

model, wiki = load_resources()

# --- UI LAYOUT ---
st.title("🧠 AI Wikipedia Speedrunner")
st.markdown("Watch an AI navigate from point A to point B using Semantic Vector Search.")

# Create columns for inputs
col1, col2 = st.columns(2) 

with col1:
    start_input = st.text_input("Start Page", placeholder="e.g. SpongeBob SquarePants")

with col2:
    target_input = st.text_input("Target Page", placeholder="e.g. Nuclear Power")

# Single Button Definition
start_btn = st.button("🚀 Start Speedrun", type="primary")

# --- EXECUTION LOGIC ---
if start_btn:
    if not start_input or not target_input:
        st.warning("Please enter both pages.")
        st.stop()

    start_title = scraper.resolve_redirect(wiki, start_input)
    target_title = scraper.resolve_redirect(wiki, target_input)
    
    # 1. CHECK MEMORY FIRST
    cached_path = database.check_memory(start_title, target_title)
    
    if cached_path:
        st.success(f"🧠 Memory Recalled! Found path in database.")
        st.write(f"**Path:** {' ➡️ '.join(cached_path)}")
        
        # Show Graph
        try:
            graph_file = visualizer.create_graph(cached_path)
            with open(graph_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=410)
        except Exception as e:
            st.warning(f"Could not generate graph: {e}")
            
    else:
        # 2. RUN AI (If not in memory)
        st.info("Thinking... (Calculating new path)")
        
        target_embedding = model.encode(target_title, convert_to_tensor=True)
        queue = [(-0.0, [start_title])]
        visited = set([start_title])
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        found_path = None
        
        steps = 0
        while queue and steps < 50:
            steps += 1
            progress_bar.progress(min(steps * 2, 100))
            
            score, path = heapq.heappop(queue)
            current_title = path[-1]
            status_text.markdown(f"Visiting: **{current_title}**")
            
            # Win Check
            if current_title.lower() == target_title.lower():
                found_path = path
                break
                
            # Fetch Links
            page = wiki.page(current_title)
            links = scraper.get_valid_links(page)
            
            # Quick Win Check
            matches = [l for l in links if l.lower() == target_title.lower()]
            if matches:
                path.append(matches[0])
                found_path = path
                break
            
            # AI Processing
            if not links: continue
            links_to_scan = links[:100]
            link_vectors = model.encode(links_to_scan, convert_to_tensor=True, show_progress_bar=False)
            
            scored = []
            for i, link in enumerate(links_to_scan):
                s = ai_logic.calculate_score(link, target_title, link_vectors[i], target_embedding)
                scored.append((s, link))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            
            # Beam Add
            added = 0
            for s, link in scored:
                if link not in visited:
                    visited.add(link)
                    new_path = list(path)
                    new_path.append(link)
                    heapq.heappush(queue, (-s, new_path))
                    added += 1
                    if added >= 3: break
        
        # 3. RESULT
        if found_path:
            st.toast("Correct Answer! 🎉")
            st.success("Target Reached!")
            st.write(f"**Path:** {' ➡️ '.join(found_path)}")
            
            # Save to Memory
            database.save_run(start_title, target_title, found_path)
            
            # Visualize
            try:
                graph_file = visualizer.create_graph(found_path)
                with open(graph_file, 'r', encoding='utf-8') as f:
                    st.components.v1.html(f.read(), height=410)
            except Exception as e:
                pass # Graph might fail on read-only systems, just ignore
        else:
            st.error("Failed to find path.")
