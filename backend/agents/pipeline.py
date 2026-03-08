import asyncio
from agents.claim_extractor import extract_and_clean_claim
from agents.news_search import search_news
from agents.fact_check import search_fact_checks
from agents.wikipedia_agent import search_wikipedia
from agents.nlp_signals import analyze_nlp_signals
from agents.gemini_verifier import verify_claim_with_gemini
from agents.response_builder import build_final_response
from database.crud import save_analysis
from typing import Optional

async def analyze_claim_pipeline(claim: str, user_id: Optional[str] = None, ip_address: Optional[str] = None):
    # 1. Clean the claim
    clean_claim = extract_and_clean_claim(claim)
    
    # 2. Extract NLP signals
    nlp_flags = analyze_nlp_signals(clean_claim)
    
    # 3. Parallel external searches
    news_task = search_news(clean_claim)
    fact_check_task = search_fact_checks(clean_claim)
    wiki_task = search_wikipedia(clean_claim)
    
    news_results, fact_check_results, wiki_results = await asyncio.gather(
        news_task, fact_check_task, wiki_task
    )
    
    all_sources = fact_check_results + news_results + wiki_results
    
    # 4. Verify with Gemini
    ai_result = await verify_claim_with_gemini(clean_claim, all_sources)
    
    # 5. Build final response
    analysis = build_final_response(
        claim=claim,
        clean_claim=clean_claim,
        ai_result=ai_result,
        sources=all_sources,
        nlp_flags=nlp_flags,
        user_id=user_id,
        ip_address=ip_address
    )
    
    # 6. Save to database (fire and forget or await)
    analysis_dict = analysis.model_dump()
    await save_analysis(analysis_dict)
    
    return analysis_dict
