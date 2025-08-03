#!/usr/bin/env python3
"""
Force clear database - removes all data with explicit commit
"""
import sqlite3
import os

def force_clear_database():
    """Force clear all data from the database tables"""
    try:
        # Connect to the database
        conn = sqlite3.connect('ads.db')
        cursor = conn.cursor()
        
        print("🗑️  Force clearing database data...")
        
        # Check current data count before clearing
        cursor.execute("SELECT COUNT(*) FROM ads")
        ads_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicle_comparisons") 
        comparisons_count = cursor.fetchone()[0]
        
        print(f"Current data:")
        print(f"  - Ads: {ads_count}")
        print(f"  - Comparisons: {comparisons_count}")
        
        if ads_count == 0 and comparisons_count == 0:
            print("✅ Database is already empty!")
            conn.close()
            return
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Clear all data from tables
        print("\n🧹 Force clearing tables...")
        
        # Delete all ads
        cursor.execute("DELETE FROM ads")
        print(f"  - Marked {cursor.rowcount} ads for deletion")
        
        # Delete all comparisons  
        cursor.execute("DELETE FROM vehicle_comparisons")
        print(f"  - Marked {cursor.rowcount} comparisons for deletion")
        
        # Commit the transaction
        cursor.execute("COMMIT")
        print("  - Changes committed to database")
        
        # Verify tables are empty
        cursor.execute("SELECT COUNT(*) FROM ads")
        final_ads = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicle_comparisons")
        final_comparisons = cursor.fetchone()[0]
        
        print(f"\n✅ Database cleared successfully!")
        print(f"Final counts:")
        print(f"  - Ads: {final_ads}")
        print(f"  - Comparisons: {final_comparisons}")
        
        # Vacuum database to reclaim space
        print("\n🔧 Optimizing database...")
        cursor.execute("VACUUM")
        print("✅ Database optimized!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        if 'conn' in locals():
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
            conn.close()

if __name__ == "__main__":
    # Check if database file exists
    if not os.path.exists('ads.db'):
        print("❌ Database file 'ads.db' not found!")
        exit(1)
    
    force_clear_database()
