#!/usr/bin/env python3
"""
Quick script to inspect the ads database table
"""
import sqlite3
import json

def inspect_ads_table():
    try:
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        
        print("🔍 Inspecting ads table...")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(ads)")
        columns = cursor.fetchall()
        print("\n📋 Table Schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM ads")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 Total ads: {total_count}")
        
        if total_count > 0:
            # Get sample records
            cursor.execute("SELECT * FROM ads LIMIT 5")
            records = cursor.fetchall()
            
            print("\n📝 Sample Records:")
            column_names = [description[0] for description in cursor.description]
            
            for i, record in enumerate(records, 1):
                print(f"\n--- Record {i} ---")
                for j, value in enumerate(record):
                    print(f"  {column_names[j]}: {value}")
        
        conn.close()
        print("\n✅ Database inspection completed")
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_ads_table()
