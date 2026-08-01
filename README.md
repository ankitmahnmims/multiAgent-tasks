# 🤖 Multi-Agent AI Job Hunt Assistant

A modular multi-agent AI system built in Python to automate repetitive job hunt tasks:
- **Cover Letter Agent**: Generates tailored cover letters and downloadable PDFs.
- **Networking Agent**: Crafts high-conversion outreach templates (LinkedIn DM & Cold Email).
- **CV Review Agent**: Performs ATS screen, 6-second recruiter evaluation, and prioritized edits.
- **Human-in-the-Loop Feedback Loop**: Iteratively refines outputs based on user feedback.

Inspired by Kaif Kohari's article *"I Built a Team of AI Agents to Automate your Job Hunt"*.

---

## 🛠️ Installation & Setup

1. **Clone repository & navigate to folder**:
   ```bash
   cd /Users/ankit/antigravity/multiAgent-tasks
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and add your OpenAI API Key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DEFAULT_MODEL=gpt-4o-mini
   ```

---

## 🚀 Running the Web Interface

Launch the Gradio dashboard locally:
```bash
python app.py
```
Open your browser at `http://localhost:7860`.

---

## 📁 Repository Structure

```
multiAgent-tasks/
├── app.py                  # Gradio Web Interface
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── README.md               # Documentation
├── tests/                  # Automated unit tests
│   └── test_system.py
└── src/
    ├── agents/             # Specialist AI agents
    │   ├── base.py         # BaseAgent & OpenAI client
    │   ├── cover_letter.py # Cover Letter generator & revision
    │   ├── networking.py   # LinkedIn DM & Cold Email generator
    │   └── cv_review.py    # ATS screen & recruiter evaluation
    ├── core/               # System orchestrator & feedback loop
    │   ├── orchestrator.py # Route & scrapers dispatch
    │   └── coordinator.py  # ReviewCoordinator feedback loop
    └── utils/              # Helper utilities
        ├── pdf_handler.py  # PDF text extraction & ReportLab PDF generator
        ├── scraper.py      # Job posting HTML web scraper
        └── contact_sniffer.py # Candidate contact details extractor
```

---

## 🧪 Running Tests

Execute unit tests:
```bash
python -m unittest discover -s tests
```
