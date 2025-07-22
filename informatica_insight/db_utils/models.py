from sqlalchemy import create_engine, Column, Integer, String, Date,ForeignKey,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class InformaticaConnectionsDetails(Base):
    __tablename__ = "informatica_connections_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_type = Column(String)  # VARCHAR2
    connection_name = Column(String)  # VARCHAR2
    user_name = Column(String)  # VARCHAR2
    connection_string = Column(String)  # VARCHAR2
    database_name = Column(String)  # VARCHAR2
    host_name = Column(String)  # VARCHAR2
    port_number = Column(Integer)  # NUMBER
    service_name = Column(String)  # VARCHAR2
    informatica_server = Column(String)  # VARCHAR
    informatica_user = Column(String)  # VARCHAR
    created_date = Column(Date)  # DATE
    updated_date = Column(Date)  # DATE


class InformaticaHierarchyStructure(Base):
    __tablename__ = "informatica_hierarchy_structure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_name = Column(String(100))  # VARCHAR2(100)
    session_wf_name = Column(String(255))  # VARCHAR2(255)
    workflow_id = Column(String(20))  # VARCHAR2(20)
    session_id = Column(String(20))  # VARCHAR2(20)
    hierarchy_structure = Column(String(500))  # VARCHAR2(500)
    path = Column(String(500))  # VARCHAR2(500)
    instance_id = Column(String(100))  # VARCHAR2(100)
    informatica_server = Column(String(200))  # VARCHAR2(200)
    informatica_user = Column(String(50))  # VARCHAR2(50)
    created_date = Column(Date)  # DATE
    updated_date = Column(Date)  # DATE


class InformaticaSessionsConnections(Base):
    __tablename__ = "informatica_sessions_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_name = Column(String(50))  # VARCHAR2(50)
    workflow_name = Column(String(100))  # VARCHAR2(100)
    workflow_id = Column(String(20))  # VARCHAR2(20)
    session_name = Column(String(200))  # VARCHAR2(200)
    connection_type = Column(String(50))  # VARCHAR2(50)
    connection_name = Column(String(50))  # VARCHAR2(50)
    dir_name = Column(String(250))  # VARCHAR2(250)
    file_name = Column(String(199))  # VARCHAR2(199)
    cmd_task_name = Column(String(100))  # VARCHAR2(100)
    cmd_name = Column(String(400))  # VARCHAR2(400)
    script_type = Column(String(50))  # VARCHAR2(50)
    informatica_server = Column(String(50))  # VARCHAR2(50)
    informatica_user = Column(String(50))  # VARCHAR2(50)
    created_date = Column(Date)  # DATE
    updated_date = Column(Date)  # DATE



class InformaticaReleatedTables(Base):
    __tablename__ = "informatica_related_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_name = Column(String(50))             # VARCHAR2(50)
    workflow_name = Column(String(100))          # VARCHAR2(100)
    session_name = Column(String(200))           # VARCHAR2(200)
    mapping_name = Column(String(200))           # VARCHAR2(100)
    source_name = Column(String(200))            # VARCHAR2(200)
    target_name = Column(String(200))
    workflow_id = Column(String(20))
    attr_value = Column(String(4000))             # VARCHAR2(400)
    informatica_server = Column(String(50))      # VARCHAR2(50)
    informatica_user = Column(String(50))        # VARCHAR2(50)
    created_date = Column(Date)                  # DATE
    updated_date = Column(Date)                  # DATE

class WorkflowRun(Base):
    __tablename__ = "workflow_run_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_name = Column(String)
    workflow_id = Column(String)
    workflow_run_id = Column(String, unique=True, index=True)
    start_time = Column(Date)
    end_time = Column(Date)
    time_in_min = Column(Float)
    day_of_week = Column(String)
    informatica_server = Column(String)
    informatica_user = Column(String)
    created_date = Column(Date)

    sessions = relationship("SessionRun", back_populates="workflow")

    def __repr__(self):
        return (
            f"<WorkflowRun(workflow_run_id='{self.workflow_run_id}', "
            f"workflow_name='{self.workflow_name}')>"
        )

class SessionRun(Base):
    __tablename__ = "session_run_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_area = Column(String)
    workflow_name = Column(String)
    workflow_id = Column(String)
    workflow_run_id = Column(String, ForeignKey("workflow_run_statistics.workflow_run_id"))
    session_name = Column(String)        # INSTANCE_NAME
    task_type_name = Column(String)      # TASK_TYPE_NAME
    run_err_code = Column(String)
    run_err_msg = Column(String)
    start_time = Column(Date)
    end_time = Column(Date)
    time_in_min = Column(Float)
    informatica_server = Column(String)
    informatica_user = Column(String)
    created_date = Column(Date)

    workflow = relationship("WorkflowRun", back_populates="sessions")

    def __repr__(self):
        return (
            f"<SessionRun(session_name='{self.session_name}', "
            f"workflow_run_id='{self.workflow_run_id}')>"
        )


AVAILABLE_TABLES = {
    "informatica_connections_details": InformaticaConnectionsDetails,
    "informatica_hierarchy_structure": InformaticaHierarchyStructure,
    "informatica_sessions_connections": InformaticaSessionsConnections,
    "informatica_related_tables": InformaticaReleatedTables,
    "workflow_run_statistics": WorkflowRun,
    "session_run_statistics": SessionRun,

}