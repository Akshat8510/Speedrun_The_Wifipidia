# 🧠 AI Wikipedia Speedrunner

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://speedrunthewifipidia-9xmzusx2yu2aqiuc2t5yue.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-Sentence--Transformers-green)
![License](https://img.shields.io/badge/License-MIT-purple)

A smart, autonomous AI agent that plays the **Wikipedia Game** (navigating from a Start Page to a Target Page using only internal links) in real-time.

Unlike traditional bots that rely on massive 60GB database dumps, this agent runs **live on the internet**, using a "Semantic Brain" to make human-like decisions about which link to click next.

**🔴[LIVE DEMO: Click here to try the AI!](https://speedrunthewifipidia-9xmzusx2yu2aqiuc2t5yue.streamlit.app/)**

---

## 🚀 Features

*   **Live Navigation:** Fetches pages dynamically using the Wikipedia API. No storage required.
*   **Semantic Vector Search:** Uses the `all-MiniLM-L6-v2` model to turn words into math. It knows that *Apple* is close to *Fruit* and *Technology*, but far from *Brick*.
*   **Hybrid Scoring System:**
    *   **Vector Similarity:** Finds conceptually related links.
    *   **Keyword Stacking:** Heavily rewards links that share unique words with the target (fixes the "Institute Trap").
    *   **Hub Strategy (The Panic Button):** If the AI gets confused, it routes through global hubs (like *India*, *Science*, *Earth*) to "zoom out" and find a new path.
*   **Beam Search:** Explores the top 4 best paths simultaneously, reducing the chance of dead ends.
*   **Visual Dashboard:** Built with Streamlit to show the AI's "thought process" in real-time.

---

## 🧠 How It Works

The AI does not cheat. It only sees what a human sees: the current page title and the links on that page. It decides where to go based on a **Priority Score**:

$$ Score = S_{vector} + S_{keywords} + S_{hub} $$

1.  **Vector Score:** It compares the "meaning" of a link to the target.
    *   *Target:* "Nuclear Physics"
    *   *Link:* "Marine Biology" (Score: 0.45 - Good, it's science)
    *   *Link:* "SpongeBob" (Score: 0.10 - Bad)
2.  **Keyword Bonus:** If the target is "Kalinga Institute", a link named "Kalinga History" gets a massive bonus because it shares the unique word "Kalinga."
3.  **Hub Rescue:** If all links look bad (low scores), the AI prioritizes major pages (Hubs) like *United States* or *India* to escape the obscure corner of Wikipedia it is stuck in.

---

## 🛠️ Installation & Local Run

If you want to run this on your own computer:

### 1. Clone the Repo
```bash
git clone https://github.com/Akshat8510/Speedrun_The_Wifipidia.git
cd Speedrun_The_Wifipidia
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## 🧪 Example Runs

| Start Page | Target Page | Result | Time |
| :--- | :--- | :--- | :--- |
| **SpongeBob SquarePants** | **Nuclear Power** | ✅ Success | ~5s |
| **Achyuta** | **Kalinga Institute of Industrial Technology** | ✅ Success | ~8s |
| **Vector** | **Complex Number** | ✅ Success | ~4s |
| **Pikachu** | **Adolf Hitler** | ✅ Success | ~12s |

---

## ⚙️ Configuration

You can tweak the AI's "Personality" in `app.py`:

```python
BEAM_WIDTH = 4        # Number of paths to explore at once. (Higher = Smarter but Slower)
MAX_STEPS = 50        # Maximum clicks before giving up.
KEYWORD_BONUS = 0.25  # How much it values matching words.
HUB_BONUS = 0.4       # How much it values escaping to "India" or "USA" when lost.
```

---

## 🤝 Contributing

Pull requests are welcome! Ideas for improvements:
*   Add a "Backtrack" feature if the AI hits a dead end.
*   Allow the AI to click `Category:` links.
*   Add a graph visualization of the path taken.

---

## 📜 License

This project is open-source and available under the **MIT License**.

Built with ❤️ by **Akshat8510** using **Streamlit** and **Sentence-Transformers**.
