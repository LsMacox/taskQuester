from typing_extensions import Optional, Annotated
from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
    Text,
    text,
    Index,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base, str_256
import datetime


t_intpk = Annotated[int, mapped_column(primary_key=True)]
t_datetime = Annotated[datetime.datetime, mapped_column()]

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("now()"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("now()"),
        onupdate=datetime.datetime.utcnow,
    )]


event_category_association = Table(
    'event_category_association',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


task_category_association = Table(
    'task_category_association',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class TasksOrm(Base):
    __tablename__ = "tasks"

    id: Mapped[t_intpk]
    task_id: Mapped[str_256]
    title: Mapped[str_256]
    due_at: Mapped[t_datetime]
    is_completed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[t_datetime]]
    is_hidden: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    categories = relationship('CategoryOrm', secondary=task_category_association, back_populates='tasks')

    __table_args__ = (
        UniqueConstraint("task_id", name="task_id_uniq"),
        Index("task_id_index", "task_id"),
    )


class EventsOrm(Base):
    __tablename__ = "events"

    id: Mapped[t_intpk]
    event_id: Mapped[str_256]
    title: Mapped[str_256]
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_datetime: Mapped[t_datetime]
    end_datetime: Mapped[Optional[t_datetime]]
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    categories = relationship('CategoryOrm', secondary=event_category_association, back_populates='events')

    __table_args__ = (
        UniqueConstraint("event_id", name="event_id_uniq"),
        Index("event_id_index", "event_id"),
    )


class CategoryOrm(Base):
    __tablename__ = "categories"

    id: Mapped[t_intpk] = mapped_column()
    name: Mapped[str_256]
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id'),  nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    events = relationship('EventsOrm', secondary=event_category_association, back_populates='categories')
    tasks = relationship('TasksOrm', secondary=task_category_association, back_populates='categories')

    parent = relationship("CategoryOrm", foreign_keys=parent_id, remote_side=id)
    children = relationship('CategoryOrm', back_populates='parent')

    __table_args__ = (
        UniqueConstraint("name", name="name_uniq"),
        Index("name_index", "name"),
        Index("parent_id_index", "parent_id"),
    )

