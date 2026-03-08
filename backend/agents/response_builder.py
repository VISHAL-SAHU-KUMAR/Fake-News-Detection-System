from database.models import Analysis, AnalysisMeta
import uuid

def build_final_response(claim: str, clean_claim: str, ai_result: dict, sources: list, nlp_flags: list, user_id: str = None, ip_address: str = None) -> Analysis:
    fact_checks_found = sum(1 for s in sources if s["type"] == "fact_check")
    news_found = sum(1 for s in sources if s["type"] == "news")
    
    meta = AnalysisMeta(
        fact_checks_found=fact_checks_found,
        news_found=news_found
    )
    
    # NLP flags are list of strings, convert to UI struct
    # AI result might also have flags, let's merge them
    final_flags = ai_result.get("flags", [])
    for flag in nlp_flags:
        final_flags.append({
            "label": flag,
            "type": "yellow" if "ALL CAPS" not in flag else "red"
        })
        
    # Map raw sources from APIs into the UI format + LLM insights
    final_sources = []
    ai_sources_dict = {s.get("name", "").lower(): s for s in ai_result.get("sources", [])}
    
    for s in sources:
        # Try to find if AI evaluated this source
        publisher_lower = s.get("publisher", "Unknown").lower()
        ai_eval = ai_sources_dict.get(publisher_lower, {})
        
        status = ai_eval.get("status", "verified" if s["type"] == "fact_check" else "partial")
        verdict = ai_eval.get("verdict", f"Found via live {s['type']} search")
        
        final_sources.append({
            "name": s.get("publisher") or s.get("title") or "Web Source",
            "verdict": verdict,
            "status": status,
            "url": s.get("url"),
            "original_type": s["type"]
        })
        
    # If no live sources, use AI's hallucinated sources as fallback (helpful for knowledge cutoff facts)
    if not final_sources:
        final_sources = ai_result.get("sources", [])
    
    analysis = Analysis(
        request_id=str(uuid.uuid4())[:8].upper(),
        claim=claim,
        clean_claim=clean_claim,
        score=ai_result.get("score", 50),
        verdict=ai_result.get("verdict", "UNVERIFIED"),
        confidence=ai_result.get("confidence", 0),
        summary=ai_result.get("summary", ""),
        hindi_summary=ai_result.get("hindi_summary", ""),
        flags=final_flags,
        indicators=ai_result.get("indicators", []),
        sources=final_sources,
        tips=ai_result.get("tips", []),
        meta=meta,
        user_id=user_id,
        ip_address=ip_address
    )
    
    return analysis
