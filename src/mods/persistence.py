# Copyright 2026 James G Willmore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime as dt
from typing import Any, TypeVar

from sqlalchemy import select, text
from sqlmodel import Session, SQLModel, create_engine

from mods.logging_config import LoggingConfig
from mods.models import ConfigurationItem

logger = LoggingConfig().get_logger()

T = TypeVar("T")


class Persistence:
    """Class for persisting data to a SQL database using SQLModel."""

    def __init__(self, db_url: str):
        """Initialize the Persistence class with a database URL.

        Args:
            db_url: Database connection URL (e.g., 'duckdb:///./data.db').
        """
        self.engine = create_engine(db_url)
        logger.info("Database engine created.")

    def create_tables(self) -> None:
        """Create all registered SQLModel tables in the database."""
        SQLModel.metadata.create_all(bind=self.engine)
        logger.info("Database tables created.")

    def get_session(self) -> Session:
        """Create and return a new database session."""
        return Session(self.engine)

    def save(self, model: Any) -> Any:
        """Save a model instance to the database.

        Args:
            model: The model instance to save.

        Returns:
            The saved model instance.
        """
        with Session(self.engine) as session:
            if hasattr(model, "last_modified"):
                model.last_modified = dt.datetime.now(
                    tz=ConfigurationItem.get_timezone()
                )
            merged_model = session.merge(model)
            session.commit()
            session.refresh(merged_model)
            logger.info(
                f"Saved model with id: {getattr(merged_model, 'id', 'unknown')}"
            )
            return merged_model

    def get_by_id(self, model_class: type[T], model_id: str) -> T | None:
        """Retrieve a model instance by its ID.

        Args:
            model_class: The model class to query.
            model_id: The ID of the model to retrieve.

        Returns:
            The model instance or None if not found.
        """
        with Session(self.engine) as session:
            instance = session.get(model_class, model_id)
            if instance is not None:
                session.expunge(instance)
            return instance

    def get_all(self, model_class: type[T]) -> list[T]:
        """Retrieve all instances of the specified model class.

        Args:
            model_class: The model class to query.

        Returns:
            List of all model instances.
        """
        with Session(self.engine) as session:
            statement = select(model_class)
            result = list(session.execute(statement).scalars().all())
            for instance in result:
                session.expunge(instance)
            return result

    def delete(self, model: Any) -> None:
        """Delete a model instance from the database.

        For joined table inheritance models (ConfigurationItem subclasses),
        deletes child table row first, then parent row, to satisfy FK constraints.

        Args:
            model: The model instance to delete.
        """
        model_id = getattr(model, "id", None)
        if model_id is None:
            return

        model_class = type(model)

        # Delete communication links referencing this item first
        if isinstance(model, ConfigurationItem):
            with Session(self.engine) as session:
                conn = session.connection()
                conn.execute(
                    text(
                        "DELETE FROM configuration_item_communications"
                        " WHERE source_id = :id OR target_id = :id"
                    ),
                    {"id": model_id},
                )
                session.commit()

        with Session(self.engine) as session:
            # For ConfigurationItem subclasses, delete child row first
            if (
                isinstance(model, ConfigurationItem)
                and hasattr(model_class, "__tablename__")
                and model_class.__tablename__ != "configuration_items"
            ):
                child_table = model_class.__tablename__
                conn = session.connection()
                conn.execute(
                    text(f"DELETE FROM {child_table} WHERE id = :id"),
                    {"id": model_id},
                )
                # DuckDB requires commit between child/parent deletes
                session.commit()

        # Delete parent row (or non-inheritance model)
        with Session(self.engine) as session:
            conn = session.connection()
            if isinstance(model, ConfigurationItem):
                conn.execute(
                    text("DELETE FROM configuration_items WHERE id = :id"),
                    {"id": model_id},
                )
                session.commit()
            else:
                instance = session.get(model_class, model_id)
                if instance is not None:
                    session.delete(instance)
                    session.commit()
        logger.info(f"Deleted model with id: {model_id}")

    def delete_by_id(self, model_class: type, model_id: str) -> None:
        """Delete a model instance by its ID.

        For joined table inheritance models (ConfigurationItem subclasses),
        deletes child table row first, then parent row, to satisfy FK constraints.

        Args:
            model_class: The model class to query.
            model_id: The ID of the model to delete.
        """
        with Session(self.engine) as session:
            model = session.get(model_class, model_id)
            if model:
                # Delete communication links referencing this item first
                if isinstance(model, ConfigurationItem):
                    conn = session.connection()
                    conn.execute(
                        text(
                            "DELETE FROM configuration_item_communications"
                            " WHERE source_id = :id OR target_id = :id"
                        ),
                        {"id": model_id},
                    )
                    session.commit()

                # For ConfigurationItem subclasses, delete child row first
                if (
                    isinstance(model, ConfigurationItem)
                    and hasattr(model_class, "__tablename__")
                    and model_class.__tablename__ != "configuration_items"
                ):
                    with Session(self.engine) as session2:
                        child_table = model_class.__tablename__
                        conn2 = session2.connection()
                        conn2.execute(
                            text(f"DELETE FROM {child_table} WHERE id = :id"),
                            {"id": model_id},
                        )
                        session2.commit()

                    # Delete parent in new session
                    with Session(self.engine) as session3:
                        conn3 = session3.connection()
                        conn3.execute(
                            text("DELETE FROM configuration_items WHERE id = :id"),
                            {"id": model_id},
                        )
                        session3.commit()
                else:
                    with Session(self.engine) as session2:
                        instance = session2.get(model_class, model_id)
                        if instance is not None:
                            session2.delete(instance)
                            session2.commit()
                logger.info(f"Deleted model with id: {model_id}")
            else:
                logger.warning(f"Model with id: {model_id} not found for deletion.")
