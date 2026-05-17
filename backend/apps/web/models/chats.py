from pydantic import BaseModel
from typing import List, Union, Optional
from peewee import *
from playhouse.shortcuts import model_to_dict

import time
import uuid

from apps.web.internal.db import DB

####################
# Chat DB Schema
####################


class Chat(Model):
    id = CharField(unique=True)
    user_id = CharField()
    title = TextField()
    chat = TextField()  # Stores JSON string of chat messages
    created_at = BigIntegerField()
    updated_at = BigIntegerField()

    class Meta:
        database = DB
        table_name = "chat"


class ChatModel(BaseModel):
    id: str
    user_id: str
    title: str
    chat: str
    created_at: int  # timestamp in seconds
    updated_at: int  # timestamp in seconds


####################
# Forms
####################


class ChatForm(BaseModel):
    chat: dict


class ChatTitleForm(BaseModel):
    title: str


class ChatResponse(BaseModel):
    id: str
    user_id: str
    title: str
    chat: dict
    created_at: int
    updated_at: int


class ChatTitleIdResponse(BaseModel):
    id: str
    title: str
    created_at: int
    updated_at: int


class ChatTable:
    def __init__(self, db):
        self.db = db
        db.create_tables([Chat])

    def insert_new_chat(self, user_id: str, form_data: ChatForm) -> Optional[ChatModel]:
        """Create a new chat entry for a user."""
        import json

        id = str(uuid.uuid4())
        chat = ChatModel(
            **{
                "id": id,
                "user_id": user_id,
                "title": (
                    form_data.chat.get("title", "New Chat")
                    if "title" in form_data.chat
                    else "New Chat"
                ),
                "chat": json.dumps(form_data.chat),
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
            }
        )

        result = Chat.create(**chat.model_dump())
        if result:
            return chat
        return None

    def update_chat_by_id(self, id: str, chat: dict) -> Optional[ChatModel]:
        """Update an existing chat by its ID."""
        import json

        try:
            query = Chat.update(
                chat=json.dumps(chat),
                title=chat.get("title", "New Chat"),
                updated_at=int(time.time()),
            ).where(Chat.id == id)
            query.execute()

            chat_obj = Chat.get_by_id(id)
            return ChatModel(**model_to_dict(chat_obj))
        except Exception:
            return None

    def get_chat_lists_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[ChatTitleIdResponse]:
        """Retrieve a paginated list of chat titles for a user."""
        return [
            ChatTitleIdResponse(**model_to_dict(chat))
            for chat in Chat.select()
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        ]

    def get_chat_by_id_and_user_id(
        self, id: str, user_id: str
    ) -> Optional[ChatModel]:
        """Retrieve a specific chat by ID, scoped to a user."""
        try:
            chat = Chat.get((Chat.id == id) & (Chat.user_id == user_id))
            return ChatModel(**model_to_dict(chat))
        except Exception:
            return None

    def delete_chat_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        """Delete a chat by ID, scoped to a user."""
        try:
            query = Chat.delete().where(
                (Chat.id == id) & (Chat.user_id == user_id)
            )
            query.execute()
            return True
        except Exception:
            return False


Chats = ChatTable(DB)
