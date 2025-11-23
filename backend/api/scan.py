import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.scan_log import AuthStatus, ContentType, ScanLog
from parsing.parser import ContentParser
from verification.verifier import ContentVerifier

router = APIRouter(prefix="/api/scan", tags=["scan"])

# Initialize services
content_parser = ContentParser()
content_verifier = ContentVerifier()


def _extract_identifier(content_type: str, parsed_data: Dict) -> str:
    """
    Extract normalized identifier for duplicate detection.

    Args:
        content_type: Type of content (BIP21, BOLT11, etc.)
        parsed_data: Parsed data dictionary

    Returns:
        Normalized identifier string or None
    """
    if content_type == "LIGHTNING_ADDRESS":
        # For Lightning addresses, use the address itself (lowercase)
        return parsed_data.get("lightning_address", "").lower()
    elif content_type == "LNURL":
        # For LNURL, use the URL or LNURL string
        return (
            parsed_data.get("url") or
            parsed_data.get("lnurl", "")
        ).lower()
    elif content_type == "BOLT11":
        # For invoices, use the invoice string (lowercase)
        return parsed_data.get("invoice", "").lower()
    elif content_type == "BIP21":
        # For Bitcoin addresses, use the address (lowercase)
        return parsed_data.get("address", "").lower()
    return None


def _check_duplicate(
    db: Session, normalized_identifier: str
) -> Dict[str, Any]:
    """
    Check if identifier has been seen before.

    Args:
        db: Database session
        normalized_identifier: Normalized identifier to check

    Returns:
        Dict with duplicate info or None if not found
    """
    if not normalized_identifier:
        return None

    existing = (
        db.query(ScanLog)
        .filter(ScanLog.normalized_identifier == normalized_identifier)
        .order_by(ScanLog.timestamp.asc())
        .first()
    )

    if existing:
        # Count total scans
        count = (
            db.query(ScanLog)
            .filter(
                ScanLog.normalized_identifier == normalized_identifier
            )
            .count()
        )

        return {
            "count": count,
            "first_seen": existing.timestamp.isoformat(),
            "first_scan_id": existing.scan_id,
        }

    return None


@router.post("/")
async def scan_content(
    request: Dict[str, Any], db: Session = Depends(get_db)
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
        try:
            parsed_data = content_parser.parse(content)
        except ValueError as ve:
            # Validation errors should return 400
            raise HTTPException(status_code=400, detail=str(ve))

        # Extract normalized identifier for duplicate detection
        normalized_identifier = _extract_identifier(
            parsed_data.get("content_type"),
            parsed_data.get("parsed_data", {})
        )

        # Check for duplicates
        duplicate_info = None
        if normalized_identifier:
            duplicate_info = _check_duplicate(
                db, normalized_identifier
            )

        # Verify content
        verification_results = await content_verifier.verify(parsed_data)

        # Add duplicate warning if found
        if duplicate_info:
            if "warnings" not in verification_results:
                verification_results["warnings"] = []
            verification_results["warnings"].insert(
                0,
                f"⚠️ This address has been scanned {duplicate_info['count']} "
                f"time(s) before. First seen: {duplicate_info['first_seen']}"
            )
            if duplicate_info["count"] >= 3:
                verification_results["warnings"].insert(
                    0,
                    "🚨 HIGH FREQUENCY: This address has been used "
                    "multiple times. Exercise caution."
                )

        # Convert string status to enum
        auth_status = AuthStatus(
            verification_results.get("auth_status", "Invalid")
        )
        content_type = ContentType(
            parsed_data.get("content_type", "UNKNOWN")
        )

        # Determine first_seen and usage_count
        first_seen = None
        usage_count = 1
        if duplicate_info:
            # This is a duplicate - get first seen from existing
            existing_first = (
                db.query(ScanLog)
                .filter(
                    ScanLog.normalized_identifier == normalized_identifier
                )
                .order_by(ScanLog.timestamp.asc())
                .first()
            )
            if existing_first and existing_first.first_seen:
                first_seen = existing_first.first_seen
            usage_count = duplicate_info["count"] + 1
        else:
            # First time seeing this identifier
            first_seen = datetime.utcnow()

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
            ip_address=request.get("ip_address"),
            normalized_identifier=normalized_identifier,
            first_seen=first_seen,
            usage_count=usage_count,
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
            "verification_results": verification_results,
            "is_duplicate": duplicate_info is not None,
            "usage_count": scan_log.usage_count,
            "first_seen": (
                scan_log.first_seen.isoformat()
                if scan_log.first_seen
                else None
            ),
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scan_id}")
async def get_scan_result(
    scan_id: str, db: Session = Depends(get_db)
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
            "outcome": scan_log.outcome,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_scan_history(
    limit: int = 10, offset: int = 0, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get scan history with pagination"""
    try:
        # Get total count
        total = db.query(ScanLog).count()

        # Get paginated results
        scan_logs = (
            db.query(ScanLog)
            .order_by(ScanLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Format response
        scans = []
        for scan_log in scan_logs:
            scans.append(
                {
                    "scan_id": scan_log.scan_id,
                    "timestamp": scan_log.timestamp.isoformat(),
                    "content_type": scan_log.content_type.value,
                    "auth_status": scan_log.auth_status.value,
                    "user_action": scan_log.user_action,
                    "outcome": scan_log.outcome,
                }
            )

        return {
            "scans": scans,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{scan_id}/action")
async def update_scan_action(
    scan_id: str, action: Dict[str, Any], db: Session = Depends(get_db)
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
            "updated": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
