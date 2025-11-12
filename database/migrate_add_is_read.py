"""
Migration script to add is_read column to messages table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from src.models.models import db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column already exists by trying to query it
        result = db.session.execute(text("PRAGMA table_info(messages)"))
        columns = [row[1] for row in result]
        
        if 'is_read' not in columns:
            # Add the column
            db.session.execute(text('ALTER TABLE messages ADD COLUMN is_read INTEGER DEFAULT 0'))
            db.session.commit()
            print('[SUCCESS] Successfully added is_read column to messages table')
        else:
            print('[INFO] is_read column already exists in messages table')
    except Exception as e:
        print(f'[ERROR] Error: {e}')
        db.session.rollback()

