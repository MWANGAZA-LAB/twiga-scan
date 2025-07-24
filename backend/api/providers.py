from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.provider import Provider

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("/")
async def list_providers(
    limit: int = 50,
    offset: int = 0,
    provider_type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List providers with filtering and pagination"""
    try:
        query = db.query(Provider)

        # Apply filters
        if provider_type:
            query = query.filter(Provider.provider_type == provider_type)
        if status:
            query = query.filter(Provider.status == status)

        # Get total count
        total = query.count()

        # Get paginated results
        providers = query.offset(offset).limit(limit).all()

        # Format response
        provider_list = []
        for provider in providers:
            provider_list.append(
                {
                    "id": provider.id,
                    "name": provider.name,
                    "domain": provider.domain,
                    "provider_type": provider.provider_type,
                    "status": provider.status,
                    "is_active": provider.is_active,
                    "created_at": (
                        provider.created_at.isoformat() if provider.created_at else None
                    ),
                }
            )

        return {
            "providers": provider_list,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_id}")
async def get_provider(
    provider_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get provider by ID"""
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        return {
            "id": provider.id,
            "name": provider.name,
            "domain": provider.domain,
            "public_key": provider.public_key,
            "certificate_fingerprint": provider.certificate_fingerprint,
            "api_url": provider.api_url,
            "provider_type": provider.provider_type,
            "status": provider.status,
            "provider_metadata": provider.provider_metadata,
            "is_active": provider.is_active,
            "created_at": (
                provider.created_at.isoformat() if provider.created_at else None
            ),
            "updated_at": (
                provider.updated_at.isoformat() if provider.updated_at else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_provider(
    provider_data: Dict[str, Any], db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new provider"""
    try:
        # Validate required fields
        required_fields = ["name", "provider_type"]
        for field in required_fields:
            if not provider_data.get(field):
                raise HTTPException(
                    status_code=400, detail=f"Field '{field}' is required"
                )

        # Check if provider with same name already exists
        existing = (
            db.query(Provider).filter(Provider.name == provider_data["name"]).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Provider with this name already exists"
            )

        # Create provider
        provider = Provider(
            name=provider_data["name"],
            domain=provider_data.get("domain"),
            public_key=provider_data.get("public_key"),
            certificate_fingerprint=provider_data.get("certificate_fingerprint"),
            api_url=provider_data.get("api_url"),
            provider_type=provider_data["provider_type"],
            status=provider_data.get("status", "trusted"),
            provider_metadata=provider_data.get("provider_metadata"),
            is_active=provider_data.get("is_active", True),
        )

        db.add(provider)
        db.commit()
        db.refresh(provider)

        return {
            "id": provider.id,
            "name": provider.name,
            "provider_type": provider.provider_type,
            "status": provider.status,
            "created": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{provider_id}")
async def update_provider(
    provider_id: int, provider_data: Dict[str, Any], db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update provider"""
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Update fields
        updateable_fields = [
            "name",
            "domain",
            "public_key",
            "certificate_fingerprint",
            "api_url",
            "provider_type",
            "status",
            "provider_metadata",
            "is_active",
        ]

        for field in updateable_fields:
            if field in provider_data:
                setattr(provider, field, provider_data[field])

        db.commit()
        db.refresh(provider)

        return {
            "id": provider.id,
            "name": provider.name,
            "provider_type": provider.provider_type,
            "status": provider.status,
            "updated": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Delete provider (soft delete by setting is_active=False)"""
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Soft delete
        provider.is_active = False
        db.commit()

        return {
            "id": provider_id,
            "deleted": True,
            "message": "Provider deactivated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types/list")
async def get_provider_types(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get list of available provider types"""
    try:
        # Get unique provider types from database
        types = db.query(Provider.provider_type).distinct().all()
        type_list = [t[0] for t in types if t[0]]

        return {
            "provider_types": type_list,
            "suggested_types": [
                "wallet",
                "exchange",
                "merchant",
                "payment_processor",
                "lightning_provider",
                "donation",
                "service",
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
