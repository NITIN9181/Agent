# Google Colab Setup Instructions

## Step 1: Install Dependencies

Run this in a Colab cell:

```python
!pip install crewai[tools] streamlit pyngrok faker pydantic nest-asyncio openai
!npm install -g localtunnel
```

## Step 2: Set Environment Variables

```python
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
```

## Step 3: Upload Project Files

Upload the entire `pronexus_agent` folder to Colab, or clone from GitHub:

```python
!git clone https://github.com/your-repo/pronexus-agent.git
%cd pronexus-agent
```

## Step 4: Run Streamlit App

```python
import subprocess
import threading

def run_streamlit():
    subprocess.run(["streamlit", "run", "src/main.py", "--server.port", "8501"])

# Start Streamlit in background
thread = threading.Thread(target=run_streamlit)
thread.daemon = True
thread.start()

# Wait a moment for Streamlit to start
import time
time.sleep(5)

# Start localtunnel
!npx localtunnel --port 8501
```

## Step 5: Access the App

1. Copy the localtunnel URL (e.g., `https://funny-cat-55.loca.lt`)
2. If prompted, enter the IP address shown in Colab
3. Access the app in your browser

## Troubleshooting

### Issue: Streamlit won't start
- Make sure port 8501 is available
- Try: `!lsof -ti:8501 | xargs kill -9` to kill existing processes

### Issue: localtunnel connection fails
- Make sure you've entered the IP address when prompted
- Try a different port: `--port 8502`

### Issue: Agents not working
- Verify OPENAI_API_KEY is set correctly
- Check that crewai is installed: `!pip show crewai`

## Alternative: Using ngrok

If localtunnel doesn't work, use ngrok:

```python
!pip install pyngrok
from pyngrok import ngrok

# Start Streamlit
# ... (same as above)

# Create tunnel
public_url = ngrok.connect(8501)
print(f"Public URL: {public_url}")
```

Note: ngrok requires free account registration.
