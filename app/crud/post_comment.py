from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.post_comment import PostComment
from app.schemas.post_comment import PostCommentCreate, PostCommentUpdate
from typing import List
from app.core.exceptions import CustomHTTPException
from sqlalchemy.orm import selectinload

async def create_comment(db: AsyncSession, user_id: str, post_id: str, data: PostCommentCreate) -> PostComment:
    try:
        comment = PostComment(user_id=user_id, post_id=post_id, content=data.content)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


async def get_comments_for_post(db: AsyncSession, post_id: str) -> List[PostComment]:
    try:
        result = await db.execute(
            select(PostComment)
            .options(selectinload(PostComment.user))
            .where(PostComment.post_id == post_id)
        )
        return result.scalars().all()
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

async def get_comment_by_id(db: AsyncSession, comment_id: str) -> PostComment | None:
    try:
        result = await db.execute(select(PostComment).where(PostComment.id == comment_id))
        return result.scalar_one_or_none()
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail=f"Failed to fetch comment by ID: {str(e)}")

async def update_comment(db: AsyncSession, comment_id: str, user_id: str, data: PostCommentUpdate) -> PostComment:
    try:
        result = await db.execute(
            select(PostComment).where(PostComment.id == comment_id, PostComment.user_id == user_id)
        )
        comment = result.scalar_one_or_none()
        if comment:
            comment.content = data.content
            await db.commit()
            await db.refresh(comment)
        return comment
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")

async def delete_comment(db: AsyncSession, comment_id: str, user_id: str) -> bool:
    try:
        result = await db.execute(
            select(PostComment).where(PostComment.id == comment_id, PostComment.user_id == user_id)
        )
        comment = result.scalar_one_or_none()
        if comment:
            await db.delete(comment)
            await db.commit()
            return True
        return False
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

