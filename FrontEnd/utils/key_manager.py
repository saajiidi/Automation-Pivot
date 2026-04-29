"""Utility class to manage widget keys to avoid collisions in Streamlit."""

class KeyManager:
    """Manages Streamlit session state keys."""
    
    @staticmethod
    def get_key(namespace: str, key_name: str) -> str:
        """Generate a namespace-prefixed key."""
        return f"{namespace}_{key_name}"