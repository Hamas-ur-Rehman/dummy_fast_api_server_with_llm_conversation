#!/usr/bin/env python3
"""
Utility functions for handling JSON message storage and retrieval
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def load_messages(filename: str = "messages.json", limit: int = 10) -> List[Dict]:
    """
    Load the most recent messages from JSON file in ascending chronological order.
    Create empty file if it doesn't exist.
    
    Args:
        filename (str): Path to the JSON file
        limit (int): Maximum number of recent messages to return (default: 10)
        
    Returns:
        list: List of the most recent messages loaded from the file, in ascending order
    """
    try:
        if not os.path.exists(filename):
            logger.info(f"Creating new messages file: {filename}")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
        
        with open(filename, "r", encoding="utf-8") as f:
            all_messages = json.load(f)
            
            # Sort by timestamp to ensure chronological order
            all_messages.sort(key=lambda x: x.get('timestamp', ''))
            
            # Get the last 'limit' messages (most recent)
            recent_messages = all_messages[-limit:] if len(all_messages) > limit else all_messages
            
            logger.info(f"Loaded {len(recent_messages)} recent messages from {filename} (total: {len(all_messages)})")
            return recent_messages
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filename}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading messages from {filename}: {e}")
        return []

def save_message(message_data: Dict, filename: str = "messages.json") -> bool:
    """
    Save a new message to the JSON file.
    
    Args:
        message_data (dict): Message data to save
        filename (str): Path to the JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing messages
        messages = load_messages(filename)
        
        # Add timestamp if not present
        if 'timestamp' not in message_data:
            message_data['timestamp'] = datetime.now().isoformat()
        
        # Append new message
        messages.append(message_data)
        
        # Save back to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved message to {filename}. Total messages: {len(messages)}")
        return True
    except Exception as e:
        logger.error(f"Error saving message to {filename}: {e}")
        return False

def get_call_history(call_id: str, filename: str = "messages.json") -> List[Dict]:
    """
    Get message history for a specific call ID.
    
    Args:
        call_id (str): The call ID to filter messages by
        filename (str): Path to the JSON file
        
    Returns:
        list: List of messages for the specified call ID
    """
    try:
        messages = load_messages(filename)
        call_messages = [msg for msg in messages if msg.get("call_id") == call_id]
        logger.info(f"Found {len(call_messages)} messages for call_id: {call_id}")
        return call_messages
    except Exception as e:
        logger.error(f"Error getting call history for {call_id}: {e}")
        return [] 