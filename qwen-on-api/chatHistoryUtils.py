from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import sessionmaker
import warnings

class ErrorOccuredWarning(Warning):
    """An error occured but it was handled by try...except"""

class PGClient:
    def __init__(self, connection_string: str):
        """
        Initialize a Client instance.

        Args:
            connection_string (str): A string representing the database connection information.

        Returns:
            None
        """
        self.engine = create_engine(connection_string)
        self.meta = MetaData(schema="public")
        self.Session = sessionmaker(self.engine)

        with self.Session() as sess:
            with sess.begin():
                sess.execute(text("create schema if not exists public;"))
    def execute_query(self, query):
        try:
            with self.Session() as sess:
                with sess.begin():
                    res = sess.execute(text(query))
            return res
        except Exception as e:
            warnings.warn(f"An error occurred: {e}", ErrorOccuredWarning)
            return None
    def disconnect(self) -> None:
        """
        Disconnect the client from the database.

        Returns:
            None
        """
        self.engine.dispose()
        return


class ConversationHistory:
    def __init__(self, client: PGClient, user_id: int):
        self.client = client
        self.user_id = user_id 
        self.client.execute_query("""DROP TABLE IF EXISTS messages;""")
        self.client.execute_query("""DROP TABLE IF EXISTS conversations;""")
        self.client.execute_query("""CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        self.client.execute_query("""CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id),
            role VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        conv_id = self.client.execute_query(f"INSERT INTO conversations (user_id) VALUES ({self.user_id}) RETURNING id")
        conversation_id = conv_id.fetchone()[0]
        self.conversation_id = conversation_id
    def add_message(self, role, content):
        content = content.replace("'","''")
        self.client.execute_query(f"INSERT INTO messages (conversation_id, role, content) VALUES ({self.conversation_id}, '{role}', '{content}')")
    def get_conversation_history(self):
        res = self.client.execute_query(f"SELECT role, content FROM messages WHERE conversation_id = {self.conversation_id} ORDER BY timestamp ASC")
        messages = res.fetchall()
        return [{"role": role, "content": content} for role, content in messages]
    