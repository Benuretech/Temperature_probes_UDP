"""
SQLAlchemy database wrapper for BlueSoft project management.
Provides ORM models and database projects for tracking intervals, passes, stations, and pulse data.
Handles database connections, CRUD project, and database updates for test projects.
"""

import os
from sqlalchemy import create_engine, Column, Integer, Float, ForeignKey, String, Boolean, JSON, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.sql import asc, case
from sqlalchemy.exc import SQLAlchemyError
import math

# ------------------------------------------------------------------------
# 1. SQLAlchemy Base and Models (ORM Classes)
# ------------------------------------------------------------------------

Base = declarative_base()

# Define the ORM classes for the database schema


class Project(Base):
    """Project Table, has a single row and represent the whole project"""

    __tablename__ = "project_table"

    project_key = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, default=0)
    date_int = Column(Integer, default=0)  # Date of the creation of the project in the format: int(datetime.datetime.now().timestamp()) (seconds since epoch)

    Name = Column(String(100), default="")
    FolderName = Column(String(100), default="")    
    FileName = Column(String(100), default="")
    Path = Column(String(100), default="")

    date_str = Column(String(100), default="")  # Date of the creation of the project in the format ("%Y-%m-%d %H_%M_%S")
    time_str = Column(String(100), default="")
    day_str = Column(String(100), default="")  # Date of the creation of the project in the format ("%Y-%m-%d")

    # Relationship to Sample
    sample_list = relationship("Sample", back_populates="project_obj", passive_deletes=True)

class Sample(Base):
    __tablename__ = "sample_table"

    sample_key = Column(Integer, primary_key=True, autoincrement=True)

    topic = Column(String(100), default="")  # Topic/sensor identifier
    value = Column(Float)
    time = Column(Float)



    project_key = Column(Integer, ForeignKey("project_table.project_key", ondelete="SET NULL"))
    project_obj = relationship("Project", back_populates="sample_list")


# ------------------------------------------------------------------------
# 2. The DataBaseWrap Class
#    Manages engine, sessions, schema creation, and CRUD methods
# ------------------------------------------------------------------------


class DataBaseWrap:
    """
    A wrapper that handles:
    - Creating or connecting to a SQLite database
    - Generating the schema
    - Providing methods to insert/fetch data
    """

    def __init__(self):
        self.linked = False
        self.engine = None
        self.SessionLocal = None
        self.db_url = None
        self.db_file_path = None
        self._current_session = None  # Track the active session
        self.project_DB = Project()

    # Database Connection and Setup Methods
    def connect_DB(self, db_file_path):
        """
        Initializes the database connection and creates the schema if necessary.

        :param db_file_path: The full path to the database file (including filename).
        """
        if self.linked:
            self.engine.dispose()
            
        # Ensure the parent directory exists
        parent_dir = os.path.dirname(db_file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        # Construct the full path for the SQLite database file.
        self.db_file_path = db_file_path
        self.db_url = f"sqlite:///{self.db_file_path}"

        # Engine and session setup.
        echo = False
        self.engine = create_engine(self.db_url, echo=echo)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Ensure the schema (all tables) exists in the database.
        # This call is safe even if the tables already exist.
        self.create_tables()
        self.linked = True

        with self.get_session() as session:
            # Retrieve the single Project row. Adjust the query if you need a specific one.
            project = session.query(Project).first()
            if project is not None:
                self.project_DB = project

    def create_tables(self):
        """Creates all tables in the database (if not exist)."""
        Base.metadata.create_all(self.engine)

    class SessionManager:
        """
        A class-based context manager to provide a SQLAlchemy session.
        """

        def __init__(self, db_wrap: "DataBaseWrap"):
            self.db_wrap = db_wrap
            self._session = None

        def __enter__(self) -> Session:
            if self.db_wrap._current_session is not None:
                # Reuse the existing session
                self._session = self.db_wrap._current_session
            else:
                # Create a new session and track it
                self._session = self.db_wrap.SessionLocal()
                self.db_wrap._current_session = self._session
            return self._session

        def __exit__(self, exc_type, exc_value, traceback):
            # Only close the session if it was created by this manager
            if self.db_wrap._current_session == self._session:
                self._session.close()
                self.db_wrap._current_session = None

    def get_session(self) -> "DataBaseWrap.SessionManager":
        """
        Returns the session manager for use in a context.
        """
        return self.SessionManager(self)

    # CRUD Methods
    def wr_project(self, Project_DB_detached=None):
        """The wr_project method is a database write project that performs a complete replacement of project data in the database.
        This method takes an optional parameter Project_DB_detached, which defaults to the instance's current project_DB if not provided."""
        if Project_DB_detached is None:
            Project_DB_detached = self.project_DB

        with self.get_session() as session:
            try:
                session.query(Project).delete()
                # Merge the project_instance into the session
                merged_project = session.merge(Project_DB_detached)

                # Commit the changes
                session.commit()
                session.refresh(merged_project)
                self.project_DB = merged_project

                return True

            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred: {e}")
                return False

