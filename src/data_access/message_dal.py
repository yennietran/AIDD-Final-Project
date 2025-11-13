"""
Data Access Layer for Message operations
Encapsulates all database interactions for Message model
"""
from src.models.models import db, Message
from typing import Optional, List


class MessageDAL:
    """Data Access Layer for Message CRUD operations"""
    
    @staticmethod
    def create(sender_id: int, receiver_id: int, content: str,
               thread_id: int = None) -> Message:
        """
        Create a new message
        
        Args:
            sender_id: ID of the message sender
            receiver_id: ID of the message receiver
            content: Message content
            thread_id: Optional thread ID for grouping messages
            
        Returns:
            Created Message object
        """
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            thread_id=thread_id
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def get_by_id(message_id: int) -> Optional[Message]:
        """Get message by ID"""
        return Message.query.get(message_id)
    
    @staticmethod
    def get_thread_messages(thread_id: int) -> List[Message]:
        """Get all messages in a thread"""
        return Message.query.filter_by(thread_id=thread_id)\
            .order_by(Message.timestamp.asc()).all()
    
    @staticmethod
    def get_user_messages(user_id: int, sent: bool = False) -> List[Message]:
        """
        Get messages for a user
        
        Args:
            user_id: User ID
            sent: If True, get sent messages; if False, get received messages
            
        Returns:
            List of Message objects
        """
        if sent:
            return Message.query.filter_by(sender_id=user_id)\
                .order_by(Message.timestamp.desc()).all()
        else:
            return Message.query.filter_by(receiver_id=user_id)\
                .order_by(Message.timestamp.desc()).all()
    
    @staticmethod
    def get_conversation(user1_id: int, user2_id: int) -> List[Message]:
        """Get conversation between two users"""
        return Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.timestamp.asc()).all()
    
    @staticmethod
    def mark_as_read(message_id: int) -> Optional[Message]:
        """Mark a message as read"""
        message = MessageDAL.get_by_id(message_id)
        if message:
            message.is_read = True
            db.session.commit()
        return message
    
    @staticmethod
    def mark_conversation_as_read(user1_id: int, user2_id: int, reader_id: int) -> int:
        """
        Mark all unread messages in a conversation as read for the specified reader
        
        Args:
            user1_id: First user ID in the conversation
            user2_id: Second user ID in the conversation
            reader_id: ID of the user who is reading (marks messages they received)
            
        Returns:
            Number of messages marked as read
        """
        # Mark all unread messages received by reader_id from the other user
        unread_messages = Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id)),
            Message.receiver_id == reader_id,
            Message.is_read == False
        ).all()
        
        count = 0
        for message in unread_messages:
            message.is_read = True
            count += 1
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread messages for a user"""
        return Message.query.filter_by(
            receiver_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def delete(message_id: int) -> bool:
        """
        Delete a message and handle all related records
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        from src.models.models import MessageReport
        
        message = MessageDAL.get_by_id(message_id)
        if not message:
            return False
        
        # Delete all message reports for this message first
        message_reports = MessageReport.query.filter_by(message_id=message_id).all()
        for report in message_reports:
            db.session.delete(report)
        
        # Now delete the message
        db.session.delete(message)
        db.session.commit()
        return True

