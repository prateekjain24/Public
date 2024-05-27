
# Create a new record
def create_record(table_name, data, supabase):
    response = supabase.table(table_name).insert(data).execute()
    if response['status_code'] == 201:
        print('Record created successfully.')
    else:
        print('Failed to create record.')

# Read records from a table
def read_records(table_name,supabase):
    response = supabase.table(table_name).select().execute()
    if response['status_code'] == 200:
        records = response['data']
        for record in records:
            print(record)
    else:
        print('Failed to fetch records.')

# Delete a record
def delete_record(table_name, record_id,supabase):
    response = supabase.table(table_name).delete().eq('id', record_id).execute()
    if response['status_code'] == 200:
        print('Record deleted successfully.')
    else:
        print('Failed to delete record.')

# Example usage
#table_name = 'users'
#data = {'name': 'John Doe', 'email': 'john.doe@example.com'}
#create_record(table_name, data)
#read_records(table_name)
#update_record(table_name, 1, {'name': 'Jane Doe'})
#delete_record(table_name, 1)