import sqlite3

conn = sqlite3.connect('ads.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:', [table[0] for table in tables])

# Check ads table structure
cursor.execute('PRAGMA table_info(ads)')
columns = cursor.fetchall()
print('Columns in ads table:')
for col in columns:
    print(f'  - {col[1]}: {col[2]}')

# Check if there are any ads
cursor.execute('SELECT COUNT(*) FROM ads')
count = cursor.fetchone()[0]
print(f'Total ads in database: {count}')

conn.close()
