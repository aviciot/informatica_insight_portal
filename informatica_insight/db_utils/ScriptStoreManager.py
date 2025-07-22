from sqlalchemy import text
from sqlalchemy.engine import Engine
from datetime import date
from informatica_insight.db_utils.db_utils2  import get_db_engine, get_config

class ScriptStoreManager:
    def __init__(self):
        self.engine = get_db_engine()
        self.config = get_config()
        self.db_type = self.config.get("insight_db.work_with", "sqlite")
        self.table_name = "script_store"

    def recreate_table(self):
        with self.engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
            self._create_table(conn)

    def create_if_not_exists(self):
        with self.engine.connect() as conn:
            self._create_table(conn)

    def _create_table(self, conn):
        if self.db_type == "sqlite":
            conn.execute(text(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name} USING fts5(
                    script_name,
                    script_path,
                    script_text,
                    informatica_server,
                    informatica_user,
                    created_date UNINDEXED,
                    updated_date UNINDEXED
                );
            """))
        elif self.db_type == "postgres":
            # Regular table with tsvector column
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    script_name TEXT,
                    script_path TEXT,
                    script_text TEXT,
                    informatica_server TEXT,
                    informatica_user TEXT,
                    created_date DATE,
                    updated_date DATE,
                    script_text_vector tsvector
                );
            """))
            # Create GIN index for full-text search
            conn.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_text_idx
                ON {self.table_name} USING GIN (script_text_vector);
            """))
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

        print(f"Table `{self.table_name}` is ready for {self.db_type}")

    def insert_script(self, script: dict):
        with self.engine.connect() as conn:
            if self.db_type == "sqlite":
                conn.execute(text(f"""
                    INSERT INTO {self.table_name} (
                        script_name,
                        script_path,
                        script_text,
                        informatica_server,
                        informatica_user,
                        created_date,
                        updated_date
                    ) VALUES (
                        :script_name, :script_path, :script_text,
                        :informatica_server, :informatica_user,
                        :created_date, :updated_date
                    );
                """), script)
            elif self.db_type == "postgres":
                # Manually populate the tsvector field
                conn.execute(text(f"""
                    INSERT INTO {self.table_name} (
                        script_name,
                        script_path,
                        script_text,
                        informatica_server,
                        informatica_user,
                        created_date,
                        updated_date,
                        script_text_vector
                    ) VALUES (
                        :script_name, :script_path, :script_text,
                        :informatica_server, :informatica_user,
                        :created_date, :updated_date,
                        to_tsvector(:script_text)
                    );
                """), script)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
