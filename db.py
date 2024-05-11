import psycopg2

# PostgreSQL connection URL
connection_url = "postgres://render_deploy_maa_user:bbVffGYP5BPMSb0dITtT5VEub65dEkPU@dpg-codue0ol5elc73fuoes0-a/render_deploy_maa"

# Establish connection
try:
    conn = psycopg2.connect(connection_url)
    print("Connected to the database!")
    
    # Now you can perform operations on the database
    
except psycopg2.OperationalError as e:
    print("Unable to connect to the database:", e)
