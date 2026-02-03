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
from typing import TypeVar

from sqlmodel import Session, SQLModel, create_engine, select

from mods.logging_config import LoggingConfig
from mods.models import ConfigurationItem

logger = LoggingConfig().get_logger()

T = TypeVar("T", bound=SQLModel)


class Persistence:
    """Class for persisting data to a SQL database using SQLModel."""

    def __init__(self, db_url: str):
        """
        Initialize the Persistence class with a database URL.
        :param db_url: Database connection URL (e.g., 'duckdb:///./data.db').
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

    def save(self, model: T) -> T:
        """
        Save a SQLModel instance to the database.
        :param model: The SQLModel instance to save.
        :return: The saved model instance.
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
        """
        Retrieve a model instance by its ID.
        :param model_class: The model class to query.
        :param model_id: The ID of the model to retrieve.
        :return: The model instance or None if not found.
        """
        with Session(self.engine) as session:
            instance = session.get(model_class, model_id)
            if instance is not None:
                session.expunge(instance)
            return instance

    def get_all(self, model_class: type[T]) -> list[T]:
        """
        Retrieve all instances of the specified model class.
        :param model_class: The model class to query.
        :return: List of all model instances.
        """
        with Session(self.engine) as session:
            statement = select(model_class)
            result = list(session.exec(statement).all())
            for instance in result:
                session.expunge(instance)
            return result

    def delete(self, model: SQLModel) -> None:
        """
        Delete a SQLModel instance from the database.
        :param model: The SQLModel instance to delete.
        """
        with Session(self.engine) as session:
            session.delete(model)
            session.commit()
            logger.info(f"Deleted model with id: {getattr(model, 'id', 'unknown')}")

    def delete_by_id(self, model_class: type[SQLModel], model_id: str) -> None:
        """
        Delete a model instance by its ID.
        :param model_class: The model class to query.
        :param model_id: The ID of the model to delete.
        """
        with Session(self.engine) as session:
            model = session.get(model_class, model_id)
            if model:
                session.delete(model)
                session.commit()
                logger.info(f"Deleted model with id: {model_id}")
            else:
                logger.warning(f"Model with id: {model_id} not found for deletion.")
