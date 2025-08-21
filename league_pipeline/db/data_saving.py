from typing import Union
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Type
from sqlalchemy.orm import DeclarativeBase
from logging import Logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert


class DataSaver:
    """
    A class for saving data to SQLite databases using SQLAlchemy ORM.
    
    This class provides methods to save both individual records and batches of data
    to database tables, with built-in conflict resolution and error handling.
    
    Attributes:
        db_location (Union[str, Path]): Path to the database directory.
        database_name (str): Name of the database file.
        engine: SQLAlchemy engine instance for database connections.
        Session: SQLAlchemy sessionmaker bound to the engine.
        sql_table_object (Type[DeclarativeBase]): SQLAlchemy model class for the target table.
        logger (Logger): Logger instance for recording operations and errors.
    
    Raises:
        ValueError: If the database engine is not SQLite.
    """
    
    def __init__(self, 
                 db_location: Union[str, Path],
                 database_name: str,
                 sql_engine_url: str,
                 sql_table_object: Type[DeclarativeBase],
                 logger: Logger) -> None:
        """
        Initialize the DataSaver with database connection and configuration.
        
        Args:
            db_location (Union[str, Path]): Path to the database directory.
            database_name (str): Name of the database file.
            sql_engine_url (str): SQLAlchemy URL string for database connection.
            sql_table_object (Type[DeclarativeBase]): SQLAlchemy model class for data insertion.
            logger (Logger): Logger instance for operation tracking.
            
        Raises:
            ValueError: If the SQL engine is not SQLite (currently only SQLite is supported).
        """
        self.db_location = db_location
        self.database_name = database_name
        self.engine = create_engine(sql_engine_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.sql_table_object = sql_table_object
        self.logger = logger

        if self.engine.dialect.name != "sqlite":
            raise ValueError("Currently only sqlite is available as the engine")

    def save_data(self, data: Union[list, dict]) -> None:
        """
        Save data to the database with conflict resolution.
        
        This method handles both single records (dict) and batch inserts (list).
        For SQLite, it uses INSERT OR IGNORE for conflict resolution on batch inserts
        and handles IntegrityError exceptions for single record inserts.
        
        Args:
            data (Union[list, dict]): Data to be saved. Can be a single dictionary
                                    representing one record, or a list of dictionaries
                                    for batch insertion.
        
        Raises:
            Exception: Re-raises any unexpected exceptions after logging and rollback.
            
        Note:
            - For list input: Uses SQLite's INSERT OR IGNORE for duplicate handling
            - For dict input: Catches IntegrityError and logs warnings for duplicates
            - All database sessions are properly managed with commit/rollback
        """
        session = self.Session()

        try:
            if isinstance(data, list):
                # Batch insert with conflict resolution
                stmt = insert(self.sql_table_object).values(data)
                stmt = stmt.on_conflict_do_nothing()
                session.execute(stmt)
                session.commit()
                
            elif isinstance(data, dict):
                # Single record insert with integrity error handling
                try:
                    record = self.sql_table_object(**data)
                    session.add(record)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    self.logger.warning("IntegrityError: duplicate or invalid data | Skipping Data")
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Unexpected error has occurred: {str(e)}")
            raise
        finally:
            session.close()
