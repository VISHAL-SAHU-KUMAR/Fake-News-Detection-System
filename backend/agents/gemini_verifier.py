import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.logger import logger
from typing import List

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def format_context(sources: List[dict]) -> str:
    if not sources:
        return "No external sources found."
    context_str = ""
    for i, s in enumerate(sources[:7]): # Limit to top 7
        context_str += f"[{i+1}] {s['type'].upper()} ({s.get('publisher', 'Unknown')}): {s.get('title', '')}\n"
        if s.get('snippet'):
            context_str += f"    Snippet: {s.get('snippet')}\n"
        if s.get('rating'):
            context_str += f"    Fact Check Rating: {s.get('rating')}\n"
    return context_str

async def verify_claim_with_gemini(claim: str, sources: List[dict]) -> dict:
    if not GOOGLE_API_KEY:
        logger.warning("Google API key missing.")
        return {
            "score": 50, "verdict": "UNVERIFIED", "confidence": 0,
            "summary": "Google API key is missing. Could not perform AI analysis.",
            "hindi_summary": "Google API key missing hai. AI analysis nahi ho paya."
        }
        
    try:
        # Use gemini-1.5-flash for speed
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1,
            max_output_tokens=2048
        )
        
        parser = JsonOutputParser()
        
        # Adding a clearer instruction for JSON-only output
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are TruthLens, the world's most advanced AI claim verification system.
            Your task is to analyze the user's claim against provided evidence and return a high-fidelity JSON report.
            
            CRITICAL: Your entire response must be a single valid JSON object. Do not include any preamble, markdown formatting (like ```json), or postscript.
            
            JSON Structure:
            {{
              "score": <0-100 score, 0=False, 100=Verified>,
              "verdict": "VERIFIED" | "MISLEADING" | "FALSE" | "UNVERIFIED",
              "confidence": <0-100 confidence value>,
              "summary": "<Expert analysis summary in 2-3 sentences>",
              "hindi_summary": "<Explanation in Hindi>",
              "flags": [
                {{"label": "<Short flag name, e.g. SENSATIONALIST>", "type": "red|yellow|green"}}
              ],
              "indicators": [
                {{"icon": "<Emoji indicator>", "title": "<Criteria name>", "desc": "<Result detail>", "status": "pass|fail|warn", "colorClass": "green|red|yellow"}}
              ],
              "sources": [
                {{"name": "<Publisher Name>", "verdict": "<What they confirm/deny>", "status": "verified|partial|false"}}
              ],
              "tips": [
                {{"text": "<Verification tip for the user>"}}
              ]
            }}
            """),
            ("user", "CLAIM TO ANALYZE: {claim}\n\nEVIDENCE RETRIEVED:\n{context}\n\nAnalyze deeply and return the report in raw JSON format.")
        ])
        
        context_str = format_context(sources)
        chain = prompt | llm | parser
        
        # We wrap in another layer of safety in case Gemini doesn't follow JSON format exactly
        result = await chain.ainvoke({
            "claim": claim,
            "context": context_str
        })
        
        return result
    except Exception as e:
        err_text = str(e)
        if "PERMISSION_DENIED" in err_text or " 403 " in err_text or err_text.startswith("403"):
            logger.error(f"Gemini access denied: {e}")
            return {
                "score": 50, "verdict": "UNVERIFIED", "confidence": 0,
                "summary": "Gemini API is not enabled for this Google Cloud project or the key has no access. Enable Generative Language API and retry.",
                "hindi_summary": "Gemini API is project ke liye enabled nahi hai ya key ko access nahi mila. Generative Language API enable karke dubara try karein.",
                "flags": [{"label": "GEMINI ACCESS DENIED", "type": "red"}],
                "indicators": [],
                "sources": [],
                "tips": [{"text": "Google Cloud Console me Generative Language API enable karein, phir app restart karke test karein."}]
            }

        logger.error(f"Critical error in Gemini Verification: {e}")
        # Return a fallback but meaningful response
        return {
            "score": 50, "verdict": "UNVERIFIED", "confidence": 0,
            "summary": "The AI analyzer encountered a structural processing error. Please retry or check back later.",
            "hindi_summary": "AI analyzer ko structural processing error mila. Fir se koshish karein.",
            "flags": [{"label": "PROCESSING ERROR", "type": "red"}],
            "indicators": [],
            "sources": [],
            "tips": [{"text": "Try a shorter, more specific claim for a cleaner analysis."}]
        }
