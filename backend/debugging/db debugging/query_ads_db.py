#!/usr/bin/env python3
"""
Query the ads.db database and print the results
"""

import sqlite3

def query_ads_db():
    """Query the ads.db database"""
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()
        
        print("📝 Querying the 'ads' table...")
        c.execute("SELECT * FROM ads ORDER BY created_at DESC LIMIT 5")
        
        rows = c.fetchall()
        
        if not rows:
            print("No ads found in the database.")
            return
        
        print(f"Found {len(rows)} ads:")
        
        for row in rows:
            print("-" * 20)
            print(f"  ID: {row[0]}")
            print(f"  Title: {row[1]}")
            print(f"  Price: {row[2]}")
            print(f"  Location: {row[3]}")
            print(f"  Mileage: {row[4]}")
            print(f"  Year: {row[5]}")
            print(f"  Link: {row[6]}")
            print(f"  Analysis Session ID: {row[7]}")
            print(f"  Vehicle Name: {row[8]}")
            print(f"  Comparison ID: {row[9]}")
            print(f"  Created At: {row[10]}")
        
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    query_ads_db()
