"""
Human Approval Webhook Server for AI Rails TDD

This server provides webhook endpoints for human approval in the TDD workflow.
It displays test results for review and waits for human approval/rejection.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Rails TDD Approval Server")

# Enable CORS for n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store pending approvals in memory (use Redis in production)
pending_approvals: Dict[str, Dict[str, Any]] = {}
approval_responses: Dict[str, Dict[str, Any]] = {}


class ApprovalRequest(BaseModel):
    """Schema for approval requests from n8n"""

    workflow_id: str
    feature_description: str
    generated_tests: str
    test_categories: list[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ApprovalResponse(BaseModel):
    """Schema for human approval responses"""

    approved: bool
    feedback: Optional[str] = None
    reviewer: str = "human"
    reviewed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "service": "AI Rails TDD Approval Server"}


@app.post("/webhook/approval-request")
async def create_approval_request(request: ApprovalRequest):
    """
    Endpoint called by n8n to create an approval request.
    Stores the request and returns an approval URL.
    """
    approval_id = str(uuid.uuid4())

    # Store the request
    pending_approvals[approval_id] = {
        "id": approval_id,
        "request": request.dict(),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    approval_url = f"http://localhost:8000/approve/{approval_id}"

    logger.info(f"Created approval request {approval_id}")

    return {
        "approval_id": approval_id,
        "approval_url": approval_url,
        "message": "Approval request created. Visit the URL to review and approve/reject.",
    }


@app.get("/approve/{approval_id}", response_class=HTMLResponse)
async def show_approval_interface(approval_id: str):
    """
    Display the approval interface for human review.
    Shows the generated tests and provides approve/reject buttons.
    """
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval = pending_approvals[approval_id]
    request_data = approval["request"]

    # Generate HTML interface
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Rails TDD - Test Approval</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; margin-top: 30px; }}
            .feature-desc {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .code-block {{
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 4px;
                overflow-x: auto;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.5;
            }}
            .checklist {{
                background: #e8f4f8;
                padding: 20px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .checklist label {{
                display: block;
                margin: 10px 0;
                cursor: pointer;
            }}
            .actions {{
                margin-top: 30px;
                display: flex;
                gap: 20px;
                align-items: flex-start;
            }}
            .feedback {{
                flex: 1;
            }}
            textarea {{
                width: 100%;
                min-height: 100px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: inherit;
                font-size: 14px;
            }}
            button {{
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s;
            }}
            .approve {{ background: #22c55e; color: white; }}
            .approve:hover {{ background: #16a34a; }}
            .reject {{ background: #ef4444; color: white; }}
            .reject:hover {{ background: #dc2626; }}
            .categories {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin: 10px 0;
            }}
            .category {{
                background: #ddd;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Test Approval Required</h1>
            
            <div class="feature-desc">
                <h3>Feature Description:</h3>
                <p>{request_data['feature_description']}</p>
            </div>
            
            <div class="categories">
                <strong>Test Categories:</strong>
                {''.join(f'<span class="category">{cat}</span>' for cat in request_data['test_categories'])}
            </div>
            
            <h2>Generated Tests:</h2>
            <pre class="code-block">{request_data['generated_tests']}</pre>
            
            <div class="checklist">
                <h3>Review Checklist:</h3>
                <label><input type="checkbox"> Tests cover happy path scenarios</label>
                <label><input type="checkbox"> Tests cover edge cases</label>
                <label><input type="checkbox"> Tests include error handling</label>
                <label><input type="checkbox"> Tests are readable and maintainable</label>
                <label><input type="checkbox"> Property-based tests included (if applicable)</label>
                <label><input type="checkbox"> No obvious test gaming opportunities</label>
            </div>
            
            <div class="actions">
                <div class="feedback">
                    <h3>Feedback (optional for approval, required for rejection):</h3>
                    <textarea id="feedback" placeholder="Enter your feedback here..."></textarea>
                </div>
            </div>
            
            <div class="actions" style="margin-top: 20px;">
                <button class="approve" onclick="submitDecision(true)">✅ Approve Tests</button>
                <button class="reject" onclick="submitDecision(false)">❌ Reject Tests</button>
            </div>
        </div>
        
        <script>
            async function submitDecision(approved) {{
                const feedback = document.getElementById('feedback').value;
                
                if (!approved && !feedback.trim()) {{
                    alert('Please provide feedback when rejecting tests');
                    return;
                }}
                
                try {{
                    const response = await fetch('/webhook/approval-response/{approval_id}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            approved: approved,
                            feedback: feedback || null,
                            reviewer: 'human'
                        }})
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        document.body.innerHTML = `
                            <div class="container">
                                <h1>✅ Decision Submitted</h1>
                                <p>Your decision has been recorded.</p>
                                <p><strong>Status:</strong> ${{approved ? 'Approved' : 'Rejected'}}</p>
                                ${{feedback ? '<p><strong>Feedback:</strong> ' + feedback + '</p>' : ''}}
                                <p style="margin-top: 20px;">You can close this window.</p>
                            </div>
                        `;
                    }} else {{
                        alert('Error submitting decision. Please try again.');
                    }}
                }} catch (error) {{
                    alert('Network error. Please check your connection.');
                }}
            }}
        </script>
    </body>
    </html>
    """

    return html


@app.post("/webhook/approval-response/{approval_id}")
async def submit_approval_response(approval_id: str, response: ApprovalResponse):
    """
    Submit the human approval decision.
    This endpoint is called when the human clicks approve/reject.
    """
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    # Update status
    pending_approvals[approval_id]["status"] = "reviewed"
    pending_approvals[approval_id]["response"] = response.dict()

    # Store response for n8n to poll
    approval_responses[approval_id] = response.dict()

    logger.info(
        f"Approval {approval_id} {'approved' if response.approved else 'rejected'}"
    )

    return {"status": "success", "message": "Approval response recorded"}


@app.get("/webhook/check-approval/{approval_id}")
async def check_approval_status(approval_id: str):
    """
    Check the status of an approval request.
    n8n can poll this endpoint to get the human decision.
    """
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval = pending_approvals[approval_id]

    return {
        "approval_id": approval_id,
        "status": approval["status"],
        "response": approval.get("response", None),
    }


@app.post("/webhook/approve-tests")
async def n8n_webhook_endpoint(request: Request):
    """
    Direct webhook endpoint for n8n Wait for Webhook node.
    This returns immediately with approval request details.
    """
    data = await request.json()

    # Create approval request
    approval_request = ApprovalRequest(
        workflow_id=data.get("workflow_id", "unknown"),
        feature_description=data.get("feature_description", ""),
        generated_tests=data.get("generated_tests", ""),
        test_categories=data.get("test_categories", []),
    )

    # Create approval
    result = await create_approval_request(approval_request)

    # Return response that n8n expects
    return {
        "approval_url": result["approval_url"],
        "approval_id": result["approval_id"],
        "message": "Visit the approval URL to review tests",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
