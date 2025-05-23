from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationRead
from app.crud import notification as notif_crud
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationRead])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Notification)
        .options(
            selectinload(Notification.actor),
            selectinload(Notification.post),
            selectinload(Notification.comment)
        )
        .where(Notification.recipient_id == str(current_user.id))
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()
    return notifications



@router.put("/{notif_id}/read", status_code=204)
async def mark_notification_as_read(
    notif_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = await notif_crud.mark_as_read(db, notif_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

