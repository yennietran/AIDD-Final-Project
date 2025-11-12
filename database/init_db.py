"""
Database initialization script
Creates the database and tables from schema.sql
"""
import sqlite3
import os
from pathlib import Path

def init_database(db_path='instance/campus_resource_hub.db'):
    """Initialize the database with schema"""
    # Create instance directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Read schema file
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    # Create connection and execute schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema (split by semicolons for multiple statements)
    cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == '__main__':
    init_database()

