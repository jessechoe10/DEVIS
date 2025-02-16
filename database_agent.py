from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import sqlite3
import json
from datetime import datetime
import pandas as pd

@dataclass
class DatabaseConfig:
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str

@dataclass
class QueryResult:
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    rows_affected: int = 0

class DatabaseAgent:
    def __init__(self):
        self.connections: Dict[str, sqlite3.Connection] = {}
        self.query_history: List[Dict[str, Any]] = []
        self.current_database: Optional[str] = None

    def process_request(self, prompt: str):
        print(f"DatabaseAgent processing request: {prompt}")
        return "DatabaseAgent response"

    def connect(self, config: DatabaseConfig) -> bool:
        """Establish a database connection"""
        try:
            if config.db_type == 'sqlite':
                conn = sqlite3.connect(config.database)
                self.connections[config.database] = conn
                self.current_database = config.database
                return True
            else:
                raise ValueError(f"Unsupported database type: {config.db_type}")
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a SQL query and return results"""
        if not self.current_database or self.current_database not in self.connections:
            return QueryResult(success=False, error="No active database connection")

        start_time = datetime.now()
        conn = self.connections[self.current_database]
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith(('SELECT', 'SHOW')):
                columns = [description[0] for description in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                result = QueryResult(
                    success=True,
                    data=data,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    rows_affected=len(data)
                )
            else:
                conn.commit()
                result = QueryResult(
                    success=True,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    rows_affected=cursor.rowcount
                )

            self._log_query(query, result)
            return result

        except Exception as e:
            return QueryResult(success=False, error=str(e))

    def create_table(self, table_name: str, columns: Dict[str, str]) -> QueryResult:
        """Create a new table with specified columns"""
        column_defs = [f"{name} {dtype}" for name, dtype in columns.items()]
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        return self.execute_query(query)

    def insert_data(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> QueryResult:
        """Insert data into a table"""
        if isinstance(data, dict):
            data = [data]

        if not data:
            return QueryResult(success=False, error="No data provided")

        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        try:
            conn = self.connections[self.current_database]
            cursor = conn.cursor()
            values = [[row[col] for col in columns] for row in data]
            cursor.executemany(query, values)
            conn.commit()
            return QueryResult(success=True, rows_affected=len(data))
        except Exception as e:
            return QueryResult(success=False, error=str(e))

    def get_table_schema(self, table_name: str) -> QueryResult:
        """Get the schema of a table"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)

    def export_to_csv(self, query: str, filepath: str) -> bool:
        """Export query results to a CSV file"""
        try:
            result = self.execute_query(query)
            if result.success and result.data:
                df = pd.DataFrame(result.data)
                df.to_csv(filepath, index=False)
                return True
            return False
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def _log_query(self, query: str, result: QueryResult):
        """Log query execution details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "success": result.success,
            "execution_time": result.execution_time,
            "rows_affected": result.rows_affected
        }
        self.query_history.append(log_entry)

    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get the query execution history"""
        return self.query_history

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the current database"""
        if not self.current_database:
            return False

        try:
            source = self.connections[self.current_database]
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False

    def optimize_query(self, query: str) -> str:
        """Simple query optimization suggestions"""
        query = query.upper()
        suggestions = []

        if "SELECT *" in query:
            suggestions.append("Consider selecting specific columns instead of using SELECT *")
        if "WHERE" not in query and ("SELECT" in query or "DELETE" in query):
            suggestions.append("Consider adding a WHERE clause to limit the scope")
        if "JOIN" in query and "INDEX" not in query:
            suggestions.append("Consider adding indexes for JOIN conditions")

        return "\n".join(suggestions) if suggestions else "No optimization suggestions"
