from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def init_database():
    # Connect to MongoDB
    client = MongoClient(os.environ.get('DATABASE_URL', 'mongodb://localhost:27017/quicksnatch'))
    db = client.quicksnatch

    try:
        # Drop existing collections
        db.users.drop()
        db.submissions.drop()
        
        # Create collections with validation
        db.create_collection('users')
        db.create_collection('submissions')
        
        # Create indexes
        db.users.create_index('team_name', unique=True)
        db.submissions.create_index([('team_id', 1), ('level', 1)])
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        
    finally:
        client.close()

if __name__ == '__main__':
    init_database()
