from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import asyncio
import os
from dotenv import load_dotenv

from database import init_db, get_db
from models import AnalysisResult, AnalysisJob
from scraper import EcommerceScraper
from analyzer import PolicyAnalyzer

load_dotenv()

app = FastAPI(
    title="E-commerce Policy Analyzer",
    description="AI-powered system for extracting and analyzing shipping and return policies",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: HttpUrl

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "E-commerce Policy Analyzer API", "version": "1.0.0"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Analyze a website's shipping and return policies"""
    try:
        job_id = await create_analysis_job(str(request.url))
        background_tasks.add_task(process_website, job_id, str(request.url))
        
        return AnalysisResponse(
            job_id=job_id,
            status="started",
            message="Analysis started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of an analysis job"""
    db = next(get_db())
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "url": job.url,
        "status": job.status,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "error_message": job.error_message
    }

@app.get("/results")
async def get_all_results():
    """Get all analysis results"""
    db = next(get_db())
    results = db.query(AnalysisResult).all()
    
    return [
        {
            "id": result.id,
            "domain": result.domain,
            "shipping_policy": result.shipping_policy,
            "shipping_url": result.shipping_url,
            "return_policy": result.return_policy,
            "return_url": result.return_url,
            "self_help_returns": result.self_help_returns,
            "self_help_url": result.self_help_url,
            "insurance": result.insurance,
            "insurance_url": result.insurance_url,
            "analyzed_at": result.analyzed_at
        }
        for result in results
    ]

@app.get("/results/{result_id}")
async def get_result(result_id: int):
    """Get a specific analysis result"""
    db = next(get_db())
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "id": result.id,
        "domain": result.domain,
        "shipping_policy": result.shipping_policy,
        "shipping_url": result.shipping_url,
        "return_policy": result.return_policy,
        "return_url": result.return_url,
        "self_help_returns": result.self_help_returns,
        "self_help_url": result.self_help_url,
        "insurance": result.insurance,
        "insurance_url": result.insurance_url,
        "analyzed_at": result.analyzed_at
    }

@app.get("/export/csv")
async def export_csv():
    """Export all results as CSV"""
    import pandas as pd
    import io
    from fastapi.responses import StreamingResponse
    
    db = next(get_db())
    results = db.query(AnalysisResult).all()
    
    # Format data according to the required CSV structure
    csv_data = []
    for result in results:
        csv_data.append({
            "domain": result.domain,
            "shipping_policy_and_cost": f"{result.shipping_policy}{result.shipping_url}",
            "return_policy_and_cost": f"{result.return_policy}{result.return_url}",
            "self_help_returns": f"{result.self_help_returns}{result.self_help_url}",
            "insurance": f"{result.insurance}{result.insurance_url}",
            "": "",
            " ": "",
            "  ": "",
            "   ": "",
            "    ": "",
            "     ": ""
        })
    
    df = pd.DataFrame(csv_data)
    
    # Create CSV string
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ecommerce_policies.csv"}
    )

@app.delete("/results/{result_id}")
async def delete_result(result_id: int):
    """Delete a specific analysis result"""
    db = next(get_db())
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    db.delete(result)
    db.commit()
    
    return {"message": f"Result {result_id} deleted successfully"}

@app.delete("/results")
async def delete_all_results():
    """Delete all analysis results"""
    db = next(get_db())
    count = db.query(AnalysisResult).count()
    db.query(AnalysisResult).delete()
    db.commit()
    
    return {"message": f"All {count} results deleted successfully"}

@app.get("/stats")
async def get_stats():
    """Get platform statistics"""
    db = next(get_db())
    
    total_sites = db.query(AnalysisResult).count()
    sites_with_self_service = db.query(AnalysisResult).filter(
        AnalysisResult.self_help_returns.like("Yes%")
    ).count()
    sites_with_insurance = db.query(AnalysisResult).filter(
        AnalysisResult.insurance.like("Yes%")
    ).count()
    
    success_rate = 100.0 if total_sites == 0 else (total_sites / total_sites) * 100
    self_service_rate = 0.0 if total_sites == 0 else (sites_with_self_service / total_sites) * 100
    insurance_rate = 0.0 if total_sites == 0 else (sites_with_insurance / total_sites) * 100
    
    return {
        "total_sites": total_sites,
        "success_rate": round(success_rate, 1),
        "self_service_rate": round(self_service_rate, 1),
        "insurance_rate": round(insurance_rate, 1),
        "sites_with_self_service": sites_with_self_service,
        "sites_with_insurance": sites_with_insurance
    }

async def create_analysis_job(url: str) -> str:
    """Create a new analysis job"""
    import uuid
    from datetime import datetime
    
    db = next(get_db())
    job_id = str(uuid.uuid4())
    
    job = AnalysisJob(
        id=job_id,
        url=url,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(job)
    db.commit()
    
    return job_id

async def process_website(job_id: str, url: str):
    """Background task to process website analysis"""
    from datetime import datetime
    
    db = next(get_db())
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    try:
        job.status = "processing"
        db.commit()
        
        # Initialize scraper and analyzer
        scraper = EcommerceScraper()
        analyzer = PolicyAnalyzer()
        
        # Scrape the website
        scraped_data = await scraper.scrape_website(url)
        
        # Analyze with AI
        analysis = await analyzer.analyze_policies(scraped_data)
        
        # Save results
        result = AnalysisResult(
            domain=analysis["domain"],
            shipping_policy=analysis["shipping_policy"],
            shipping_url=analysis["shipping_url"],
            return_policy=analysis["return_policy"],
            return_url=analysis["return_url"],
            self_help_returns=analysis["self_help_returns"],
            self_help_url=analysis["self_help_url"],
            insurance=analysis["insurance"],
            insurance_url=analysis["insurance_url"],
            analyzed_at=datetime.utcnow()
        )
        
        db.add(result)
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
