# configs/review_state_manager.py
import os
import redis
from typing import Optional
from langchain_core.messages import HumanMessage
from States.state import RedisStorageState


class ReviewStateManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=11598,
            decode_responses=True,
            username="default",
            password=os.getenv("REDIS_PASSWORD"),
        )

    def save(self, comment_id: str, state: RedisStorageState, hours: int = 24):
        """Save ReviewState to Redis"""
        key = f"review_state:{comment_id}"
        self.redis.setex(key, hours * 3600, state.model_dump_json())
        print(f"✅ Saved review state for {comment_id}")

    def get(self, comment_id: str) -> Optional[RedisStorageState]:
        """Get RedisStorageState from Redis"""
        key = f"review_state:{comment_id}"
        data = self.redis.get(key)
        if data:
            print(f"✅ Retrieved review state for {comment_id}")
            return RedisStorageState.model_validate_json(data)
        else:
            print(f"❌ No review state found for {comment_id}")
            return None

    def update(self, comment_id: str, state: RedisStorageState, hours: int = 24):
        """Update existing RedisStorageState (same as save)"""
        return self.save(comment_id, state, hours)

    def delete(self, comment_id: str):
        """Delete RedisStorageState from Redis"""
        key = f"review_state:{comment_id}"
        result = self.redis.delete(key)
        print(f"✅ Deleted review state for {comment_id}" if result else f"❌ Nothing to delete for {comment_id}")

    def exists(self, comment_id: str) -> bool:
        """Check if RedisStorageState exists"""
        key = f"review_state:{comment_id}"
        return bool(self.redis.exists(key))

redis_map = ReviewStateManager()


# Usage Example
if __name__ == "__main__":
    # Initialize manager
    state_manager = ReviewStateManager()

    # Test connection
    try:
        state_manager.redis.ping()
        print("✅ Redis connection successful!")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

    #
    #
    # # Example with your RedisStorageState
    # review_state = RedisStorageState(
    #     current_file_index=0,
    #     current_chunk_index=0,
    #     comments=[],
    #     messages=[HumanMessage(content="This is a test message")],
    # )
    #
    # # Save RedisStorage state
    # state_manager.save("comment_123", review_state, hours=48)
    #
    # # Get review state for reply
    retrieved_state = state_manager.get(2249296947)
    if retrieved_state:
        print(f"Messages count: {len(retrieved_state.messages)}")
        print("First message content:", retrieved_state.messages[0].content if retrieved_state.messages else "No messages")
