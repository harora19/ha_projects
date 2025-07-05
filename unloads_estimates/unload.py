import os
import sys
import psycopg2
from psycopg2 import pool
import threading
import hvac
import rs_tab_list
import time

user_rs=sys.argv[1]
aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']
VAULT_URL = os.environ.get('VAULT_URL')
VAULT_SECRET_ID = os.environ['VAULT_SECRET_ID']
VAULT_APPROLE = os.environ['VAULT_APPROLE']
current_directory = os.getcwd()
ssl_url = os.environ.get('SSL_URL')
verify_ssl = current_directory + '/cert.pem'
os.system(f"curl {ssl_url} > {current_directory}/cert.pem")

client = hvac.Client(url=VAULT_URL, verify=verify_ssl)
client.auth.approle.login(role_id=VAULT_APPROLE,secret_id=VAULT_SECRET_ID)
client.is_authenticated()
items = client.secrets.kv.read_secret_version(
        path="plt-infra/devops-automation/rs_stage", mount_point="apps/", raise_on_deleted_version=True
    )
pass_dw = items['data']['data']['dw_stage']
pass_dw_stg = items['data']['data']['dw_stg_stage']
s3_prefix = f'test_unload/{user_rs}/'
host_rs = os.environ['redshift_host_url']
dbname_rs = 'dw'
port_rs = 5432

if user_rs == 'dw':
    password_rs = pass_dw
else:
    password_rs = pass_dw_stg 

threaded_postgreSQL_pool = psycopg2.pool.ThreadedConnectionPool(6, 30, user=user_rs,
                                                                password=password_rs,
                                                                host=host_rs,
                                                                port=port_rs,
                                                                database=dbname_rs)

def unload_table_to_s3(table_name, s3_prefix):
    # Connect to Redshift
    conn = threaded_postgreSQL_pool.getconn()
    # print("Successfully recieved connection from threaded connection pool {}".format(conn))
    cursor = conn.cursor()

    # Unload data to S3
    unload_query = f"""
    UNLOAD ('SELECT * FROM {table_name}')
    TO 's3://bi-stage-work/{s3_prefix}'
    CREDENTIALS 'aws_access_key_id={aws_access_key_id};aws_secret_access_key={aws_secret_access_key}'
    format AS parquet allowoverwrite;
    """
    cursor.execute(unload_query)

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    threaded_postgreSQL_pool.putconn(conn)

# Specify the table name and S3 prefix

def unload_dw():
    if user_rs == 'dw':
        for x in rs_tab_list.rs_tab:              
            if x.split('.')[0] == 'dw':
                unload_table_to_s3(x, s3_prefix)
                print("table unloaded: {}".format(x))
                time.sleep(1)
                            
            elif x[0] == x[-1]:
                print("all tables unloaded")
            
            else:
                print("Skipping, table is either secure or not in schema {} | table name is: {}".format(user_rs,x))
                time.sleep(1)

def unload_dw_stg():
    if user_rs == 'dw_stg':
        for x in rs_tab_list.rs_tab:              
            if x.split('.')[0] == 'dw_stg':
                unload_table_to_s3(x, s3_prefix)
                print("table unloaded: {}".format(x))
                time.sleep(1)
                            
            elif x[0] == x[-1]:
                print("all tables unloaded for user {}".format(user_rs))
            
            else:
                print("Skipping, table is either secure or not in schema {} | table name is: {}".format(user_rs,x))
                time.sleep(1)

# Create thread objects
thread1 = threading.Thread(target=unload_dw)
thread2 = threading.Thread(target=unload_dw_stg)

# Start the threads
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()
if threaded_postgreSQL_pool:
    threaded_postgreSQL_pool.closeall
print("Threaded Redshift connection pool is closed")

# if __name__ == "__main__":
#     main()

