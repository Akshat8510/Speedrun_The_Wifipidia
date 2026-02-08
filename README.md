# 🧠 AI Wikipedia Speedrunner Pro

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://speedrunthewifipidia-9xmzusx2yu2aqiuc2t5yue.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-Sentence--Transformers-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-purple)

A smart, autonomous AI agent that plays the **Wikipedia Game** (navigating from a Start Page to a Target Page using only internal links).

This is the **Pro Version** of the speedrunner. Unlike basic bots, this version features **Long-Term Memory (SQLite)**, **Interactive Graph Visualization**, and a modular architecture. It runs **live on the internet** without needing massive database dumps.

**🔴 [LIVE DEMO: Click here to try the AI!]([https://wifispeedrunner8510.streamlit.app/])**

---

## 🚀 Pro Features

*   **🧠 Semantic Brain:** Uses `all-MiniLM-L6-v2` to understand conceptual relationships (e.g., *King* is close to *Queen*).
*   **💾 Long-Term Memory:** Uses a local **SQLite Database**. If the AI solves a path once, it remembers it forever. The next time you ask for that path, it loads instantly!
*   **🕸️ Interactive Graphs:** Generates dynamic HTML network graphs (using Pyvis) to visualize the exact path the AI took.
*   **⚡ Hybrid Scoring:**
    *   **Vector Similarity:** Finds conceptually related links.
    *   **Keyword Stacking:** Rewards unique word matches (fixes the "Institute/University" trap).
    *   **Hub Strategy:** Uses a "Panic Button" to route through global hubs (e.g., *India*, *Science*) if confused.
*   **🐳 Dockerized:** Fully containerized for easy deployment anywhere.

---

## 📂 Project Structure

The project has been refactored from a single script into a professional modular architecture:

```text
Speedrun_The_Wifipidia/
│
├── src/
│   ├── ai_logic.py      # The Brain: Vector embedding & scoring math
│   ├── scraper.py       # The Hands: Live Wikipedia API interaction
│   ├── database.py      # The Memory: SQLite handling for saving runs
│   └── visualizer.py    # The Eyes: Network graph generation
│
├── app.py               # The Interface: Streamlit Dashboard
├── Dockerfile           # Production container configuration
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

---

## 🛠️ Installation & Usage

### Method 1: Local Python Run
```bash
# 1. Clone the repo
git clone https://github.com/Akshat8510/Speedrun_The_Wifipidia.git
cd Speedrun_The_Wifipidia

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

### Method 2: Docker Run (Recommended for Deployment)
```bash
# 1. Build the image
docker build -t wiki-speedrunner .

# 2. Run the container
docker run -p 8501:8501 wiki-speedrunner
```
Access the app at `http://localhost:8501`.

---

## 🧠 The Logic (How it thinks)

The AI uses a **Beam Search** algorithm with a custom priority score:

$$ Score = S_{vector} + S_{keywords} + S_{hub} $$

1.  **Check Memory:** First, it queries `history.db`. If the path exists, return it instantly.
2.  **Scan Links:** If new, it fetches live links from the current Wikipedia page.
3.  **Evaluate:**
    *   *Vector Score:* Is the link conceptually close? (e.g., *Physics* -> *Math*)
    *   *Keyword Bonus:* Does the link share unique words with the target?
    *   *Hub Rescue:* If scores are low, jump to a Hub (e.g., *United States*) to reset context.
4.  **Visualize:** Once the target is found, it draws the path using `networkx` and `pyvis`.

---

## 🧪 Example Benchmarks

| Start Page | Target Page | Result | Logic Used |
| :--- | :--- | :--- | :--- |
| **SpongeBob SquarePants** | **Nuclear Power** | ✅ Success | Vector Similarity |
| **Achyuta** | **KIIT University** | ✅ Success | Hub Strategy (via "India") |
| **Vector** | **Complex Number** | ✅ Success | Keyword Disambiguation |
| **Pikachu** | **Adolf Hitler** | ✅ Success | Hub Strategy (via "Japan") |

---

## ⚙️ Configuration

You can tweak the AI's "Personality" in `src/ai_logic.py`:

```python
GLOBAL_HUBS = {"india", "united states", "science", ...} # Add more hubs here
```
Or in `app.py`:
```python
BEAM_WIDTH = 3        # Higher = Smarter but Slower
MAX_STEPS = 50        # Max depth
```

---

## 📜 License

This project is open-source and available under the **MIT License**.

Built with ❤️ by **Akshat8510**.
