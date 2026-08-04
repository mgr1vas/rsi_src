import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load your credentials from .env
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file!")

# 2. Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_insert():
    print("Attempting to write test data to Supabase...")
    
    # Payload matching our test table structure
    test_data = {
        "message": "Hello from the RSI backend script!"
    }
    
    try:
        # Write to the 'connection_test' table
        response = supabase.table('connection_test').insert(test_data).execute()
        
        print("\n Success! Data written to database.")
        print("Response from Supabase:")
        print(response.data)
        
    except Exception as e:
        print("\n Insert failed!")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_insert()