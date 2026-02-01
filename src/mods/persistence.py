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
from sqlmodel import Session, SQLModel, create_engine, select

from mods.logging_config import LoggingConfig
from mods.models import ConfigurationItem

logger = LoggingConfig().get_logger()


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

    def save(self, model: ConfigurationItem) -> ConfigurationItem:
        """
        Save a ConfigurationItem instance to the database.
        :param model: The ConfigurationItem instance to save.
        """
        with Session(self.engine) as session:
            merged_model = session.merge(model)
            session.commit()
            session.refresh(merged_model)
            logger.info(f"Saved model with id: {merged_model.id}")
            return merged_model

    def get_by_id(self, model_id: str) -> ConfigurationItem | None:
        """
        Retrieve a ConfigurationItem by its ID.
        :param model_id: The ID of the ConfigurationItem to retrieve.
        """
        with Session(self.engine) as session:
            instance = session.get(ConfigurationItem, model_id)
            if instance is not None:
                # Detach the instance so it can be safely used after the session closes.
                session.expunge(instance)
            return instance

    def get_all(self) -> list[ConfigurationItem]:
        """
        Retrieve all ConfigurationItem instances.
        :return: List of all ConfigurationItem instances.
        """
        with Session(self.engine) as session:
            statement = select(ConfigurationItem)
            return list(session.exec(statement).all())

    def delete(self, model: ConfigurationItem) -> None:
        """
        Delete a ConfigurationItem instance from the database.
        :param model: The ConfigurationItem instance to delete.
        """
        with Session(self.engine) as session:
            session.delete(model)
            session.commit()
            logger.info(f"Deleted model with id: {model.id}")

    def delete_by_id(self, model_id: str) -> None:
        """
        Delete a ConfigurationItem by its ID.
        :param model_id: The ID of the ConfigurationItem to delete.
        """
        with Session(self.engine) as session:
            model = session.get(ConfigurationItem, model_id)
            if model:
                session.delete(model)
                session.commit()
                logger.info(f"Deleted model with id: {model_id}")
            else:
                logger.warning(f"Model with id: {model_id} not found for deletion.")
