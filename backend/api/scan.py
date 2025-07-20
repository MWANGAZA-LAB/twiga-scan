from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime

from backend.models.database import get_db
from backend.models.scan_log import ScanLog, AuthStatus, ContentType
from backend.parsing.parser import ContentParser
from backend.verification.verifier import ContentVerifier

router = APIRouter(prefix="/api/scan", tags=["scan"])

# Initialize services
content_parser = ContentParser()
content_verifier = ContentVerifier()


@router.post("/")
async def scan_content(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Scan and verify QR/URL content
    
    Request body:
    {
        "content": "string",  # QR code content or URL
        "device_id": "string",  # Optional device identifier
        "ip_address": "string"  # Optional IP address
    }
    """
    try:
        content = request.get("content", "").strip()
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Parse content
        parsed_data = content_parser.parse(content)
        
        # Verify content
        verification_results = await content_verifier.verify(parsed_data)
        
        # Convert string status to enum
        auth_status = AuthStatus(verification_results.get("auth_status", "Invalid"))
        content_type = ContentType(parsed_data.get("content_type", "UNKNOWN"))
        
        # Save to database
        scan_log = ScanLog(
            scan_id=scan_id,
            raw_content=content,
            content_type=content_type,
            parsed_data=parsed_data.get("parsed_data"),
            auth_status=auth_status,
            verification_results=verification_results,
            warnings=verification_results.get("warnings"),
            device_id=request.get("device_id"),
            ip_address=request.get("ip_address")
        )
        db.add(scan_log)
        db.commit()
        db.refresh(scan_log)
        
        # Prepare response
        response = {
            "scan_id": scan_id,
            "timestamp": datetime.utcnow().isoformat(),
            "content_type": parsed_data.get("content_type"),
            "parsed_data": parsed_data.get("parsed_data"),
            "provider": verification_results.get("provider_known"),
            "auth_status": verification_results.get("auth_status"),
            "warnings": verification_results.get("warnings", []),
            "verification_results": verification_results
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scan_id}")
async def get_scan_result(
    scan_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get scan result by ID"""
    try:
        scan_log = db.query(ScanLog).filter(ScanLog.scan_id == scan_id).first()
        if not scan_log:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return {
            "scan_id": scan_log.scan_id,
            "timestamp": scan_log.timestamp.isoformat(),
            "content_type": scan_log.content_type.value,
            "parsed_data": scan_log.parsed_data,
            "auth_status": scan_log.auth_status.value,
            "verification_results": scan_log.verification_results,
            "warnings": scan_log.warnings,
            "user_action": scan_log.user_action,
            "outcome": scan_log.outcome
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_scan_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get scan history with pagination"""
    try:
        # Get total count
        total = db.query(ScanLog).count()
        
        # Get paginated results
        scan_logs = db.query(ScanLog).order_by(
            ScanLog.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        # Format response
        scans = []
        for scan_log in scan_logs:
            scans.append({
                "scan_id": scan_log.scan_id,
                "timestamp": scan_log.timestamp.isoformat(),
                "content_type": scan_log.content_type.value,
                "auth_status": scan_log.auth_status.value,
                "user_action": scan_log.user_action,
                "outcome": scan_log.outcome
            })
        
        return {
            "scans": scans,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{scan_id}/action")
async def update_scan_action(
    scan_id: str,
    action: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update scan action (approved, aborted, etc.)"""
    try:
        scan_log = db.query(ScanLog).filter(ScanLog.scan_id == scan_id).first()
        if not scan_log:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Update action
        scan_log.user_action = action.get("action")
        scan_log.outcome = action.get("outcome")
        db.commit()
        
        return {
            "scan_id": scan_id,
            "action": scan_log.user_action,
            "outcome": scan_log.outcome,
            "updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 