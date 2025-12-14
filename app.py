from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import google.generativeai as genai
import re

# configure Google Gemini API
genai.configure(api_key="your_api")

app = FastAPI()
frontend_path = Path(r"B:\project\kamra\advisor\frontend")

@app.get("/")
async def index():
    return FileResponse(frontend_path / "index.html")

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.post("/api/complete-profile")
async def complete_profile(request: Request):
    data = await request.json()
    profile = data.get("profile", {})
    question = data.get("question", "")

    # 🔹 your original prompt unchanged
    system_prompt = """
    You are "CareerGen", a neutral and evidence-based career and education advisor for India.
    Based on the user profile, generate a personalized career & education plan with:

    1. Top 3 career options – title and why suitable.
    2. Education/skill path for each career – include degree/cert, duration, India-relevant provider, course links, and estimated costs.
    3. First 3 concrete actions to take in the next 30 days.
    4. Recommended communities or forums for networking in each field.

    Respond in clean Markdown format with headings:
    ## Career Options
    ## Education & Skill Paths
    ## Next 30-Day Actions
    ## Communities & Networking
    """

    user_profile = "\n".join([f"{k}: {v}" for k, v in profile.items()])

    prompt = (
        system_prompt
        + "\n\nUser profile:\n" + user_profile
        + ("\n\nUser question:\n" + question if question else "")
    )

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # normalize spacing but keep Markdown intact
    text = response.text.strip()
    text_clean = re.sub(r"\n{3,}", "\n\n", text)

    return JSONResponse({"recommendation": text_clean})
