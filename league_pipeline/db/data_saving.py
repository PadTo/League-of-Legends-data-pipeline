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
    def __init__(self, 
                 db_location: Union[str, Path],
                 database_name: str,
                 sql_engine_url: str,
                 sql_table_object: Type[DeclarativeBase],
                 logger: Logger) -> None:
        
        self.db_location = db_location
        self.database_name = database_name
        self.engine = create_engine(sql_engine_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.sql_table_object = sql_table_object
        self.logger = logger


        if self.engine.dialect.name != "sqlite":
            raise ValueError("Currently only sqlite is available as the engine")


    def save_data(self, data: Union[list,dict]) -> None:
        session = self.Session()

        try:
            if isinstance(data,list):
                
                stmt = insert(self.sql_table_object).values(data)
                stmt = stmt.on_conflict_do_nothing()
                session.execute(stmt)
                session.commit()
                
            elif isinstance(data, dict):
                try:
                    record = self.sql_table_object(**data)
                    session.add(record)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    self.logger.warning("IntegrityError: duplicate or invalid data | Skipping Data")
                
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Unexpected error has occured: {str(e)}")
            raise
