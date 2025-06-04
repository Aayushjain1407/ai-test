"""
Memory database module for storing generation history.
Uses SQLite for persistent storage.
"""
import os
import sqlite3
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any


class MemoryDB:
    def __init__(self, db_path: str):
        """Initialize the memory database.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create the generations table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            prompt TEXT,
            enhanced_prompt TEXT,
            image_path TEXT,
            model_3d_path TEXT,
            created_at TIMESTAMP,
            metadata TEXT
        )
        ''')
        
        # Create users table for session management
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            created_at TIMESTAMP,
            last_active TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logging.info(f"Memory database initialized at {self.db_path}")
    
    def save_generation(self, 
                       generation_id: str,
                       user_id: str,
                       prompt: str,
                       enhanced_prompt: str = None,
                       image_path: str = None,
                       model_3d_path: str = None,
                       metadata: Dict = None) -> None:
        """Save a new generation to the database.
        
        Args:
            generation_id (str): Unique ID for the generation
            user_id (str): ID of the user who created this generation
            prompt (str): Original user prompt
            enhanced_prompt (str, optional): Enhanced prompt after LLM processing
            image_path (str, optional): Path to the generated image
            model_3d_path (str, optional): Path to the generated 3D model
            metadata (Dict, optional): Additional metadata for the generation
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {})
        
        cursor.execute(
            '''
            INSERT OR REPLACE INTO generations
            (id, user_id, prompt, enhanced_prompt, image_path, model_3d_path, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (generation_id, user_id, prompt, enhanced_prompt, image_path, model_3d_path, created_at, metadata_json)
        )
        
        conn.commit()
        conn.close()
        logging.info(f"Saved generation {generation_id} to memory")
    
    def get_generation(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific generation by ID.
        
        Args:
            generation_id (str): ID of the generation to retrieve
            
        Returns:
            Dict or None: Generation data if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM generations WHERE id = ?', (generation_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        result = dict(row)
        result['metadata'] = json.loads(result['metadata'])
        
        conn.close()
        return result
    
    def get_user_generations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all generations for a specific user.
        
        Args:
            user_id (str): User ID to filter by
            
        Returns:
            List[Dict]: List of generation records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM generations WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            item = dict(row)
            item['metadata'] = json.loads(item['metadata'])
            result.append(item)
        
        conn.close()
        return result
    
    def search_generations(self, query: str) -> List[Dict[str, Any]]:
        """Search generations by prompt text.
        
        Args:
            query (str): Search query to match against prompts
            
        Returns:
            List[Dict]: Matching generation records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple search implementation
        search_param = f"%{query}%"
        cursor.execute(
            'SELECT * FROM generations WHERE prompt LIKE ? OR enhanced_prompt LIKE ? ORDER BY created_at DESC',
            (search_param, search_param)
        )
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            item = dict(row)
            item['metadata'] = json.loads(item['metadata'])
            result.append(item)
        
        conn.close()
        return result


# Singleton instance
_memory_db = None

def get_memory_db(db_path: str = None) -> MemoryDB:
    """Get or create a singleton instance of the memory database.
    
    Args:
        db_path (str, optional): Path to the database file, only used on first call
        
    Returns:
        MemoryDB: Singleton memory database instance
    """
    global _memory_db
    if _memory_db is None:
        db_path = db_path or os.environ.get('MEMORY_DB_PATH', 'memory.db')
        _memory_db = MemoryDB(db_path)
    return _memory_db
