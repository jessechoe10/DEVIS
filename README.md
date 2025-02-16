# D.E.V.I.S
## Design Evolution Via Intelligent Systems

DEVIS is a multi-agent system that helps create and deploy UI/UX designs through voice interaction and AI-powered code generation.

### Components

1. **Voice Agent**: Captures and processes verbal feedback from engineers
2. **Frontend Agent**: Generates React components and styles based on requirements
3. **Screenshot Agent**: Captures and analyzes reference designs using Anthropic's Claude
4. **Deployment Agent**: Automatically deploys generated code to GitHub and Vercel

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following keys:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GITHUB_TOKEN=your_github_token
VERCEL_TOKEN=your_vercel_token
```

3. Install system dependencies for PyAudio:
```bash
brew install portaudio
```

### Usage

1. Run the main script:
```bash
python main.py
```

2. Speak your UI/UX requirements when prompted
3. Optionally provide a reference URL for design inspiration
4. The system will:
   - Process your voice input
   - Generate React components and styles
   - Create a GitHub repository
   - Deploy to Vercel automatically

### Example

```python
from devis import DEVIS

devis = DEVIS()
devis.run_design_cycle(reference_url="https://example.com")
```

### Notes

- Make sure your microphone is properly configured
- Ensure you have sufficient permissions for GitHub and Vercel APIs
- The generated code uses React and Tailwind CSS by default