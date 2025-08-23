import sqlite3
from datetime import datetime

conn = sqlite3.connect('back_end/light_posts.db')
cursor = conn.cursor()
def create_table_for_month(year, month,new_cursor=cursor,new_conn=conn):
    """
    Create a table for the specified year and month.
    """
    table_name = f'Light_Post{year}{month:02d}'
    new_cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            IPAddress TEXT NOT NULL,
            Energy REAL,
            InstallationDate DATE,
            LastRepairedDate DATE
        )
    ''')
    new_conn.commit()
    return table_name

def search_data(table_name, column_name, search_value,new_cursor=cursor):
    """
    Search for data in the specified column of the given table.
    """
    query = f'SELECT * FROM {table_name} WHERE {column_name} = ?'
    new_cursor.execute(query, (search_value,))
    return new_cursor.fetchall()

# Connect to the SQLite database (create a new one if not exists)


# Example usage


def insert_light_post(name, ip_address, energy, installation_date, last_repaired_date, table_name,new_cursor=cursor,new_conn=conn):
    """
    Insert a new light post into the specified month's table.
    """
    new_cursor.execute(f'''
        INSERT INTO {table_name} (Name, IPAddress, Energy, InstallationDate, LastRepairedDate)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, ip_address, energy, installation_date, last_repaired_date))
    new_conn.commit()
    print('done')

def retrieve_light_posts(table_name):
    """
    Retrieve all light posts from the specified month's table.
    """
    cursor.execute(f'SELECT * FROM {table_name}')
    return cursor.fetchall()

def edit_light_post(post_id, name, ip_address, energy, installation_date, last_repaired_date, table_name, new_cursor=cursor, new_conn=conn):
    """
    Edit the data of a specific light post in the specified month's table.
    """
    new_cursor.execute(f'''
        UPDATE {table_name}
        SET Name=?, IPAddress=?, Energy=?, InstallationDate=?, LastRepairedDate=?
        WHERE ID=?
    ''', (name, ip_address, energy, installation_date, last_repaired_date, post_id))
    new_conn.commit()

def delete_light_posts(table_name, new_cursor=cursor, new_conn=conn):
        """
        Delete all light posts from the specified month's table.
        """
        new_cursor.execute(f'DELETE FROM {table_name}')
        new_conn.commit()
        print('done')

# Example usage
# current_year = datetime.now().year
# current_month = datetime.now().month
# table_name = create_table_for_month(current_year, current_month)

# insert_light_post('LP/1', '192.879.236', 2.89, '01-01-2024', '00-00-0000', table_name)
# insert_light_post('LP/2', '192.879.285', 2.87, '01-01-2024', '00-00-0000', table_name)
# insert_light_post('LP/3', '192.879.396', 2.88, '01-01-2024', '00-00-0000', table_name)
# insert_light_post('LP/4', '192.879.342', 2.88, '01-01-2024', '00-00-0000', table_name)
# insert_light_post('LP/5', '192.879.125', 2.87, '01-01-2024', '00-00-0000', table_name)



# insert_light_post('ALL', '000.000.000', 0.0, '00-00-0000', '00-00-0000', table_name)
# # insert_light_post('LP2', '192.879.567', 0.0, '2023-03-01', '2023-04-01', table_name)

# # # # Display the original data
# print("Original Data:")
# light_posts = retrieve_light_posts(table_name)
# for post in light_posts:
#     print(post)

# # Edit the first light post
# edit_light_post(1, 'UpdatedLightPost1', '192.168.0.1', 120, '2023-01-15', '2023-02-15', table_name)

# # Display the updated data
# print("\nUpdated Data:")
# light_posts = retrieve_light_posts(table_name)
# print(type(light_posts))
# for post in light_posts:
#     print(post)

# # Search for data in the 'Name' column
# search_column = 'Name'
# search_value = 'LightPost3'
# result = search_data(table_name, search_column, search_value)
# print(type(result))
# # Display search result
# print(f"\nSearch Result for {search_column}='{search_value}':")
# for item in result:
#     print(item)

# Close the connection when done
# conn.close()