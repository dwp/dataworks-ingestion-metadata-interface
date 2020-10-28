import mysql.connector
import mysql.connector.pooling


# Runs the alter reconciliation stored procedure for local dev/testing.
def main():
    connection = mysql.connector.connect(host="localhost",
                                         user="root",
                                         password="password",
                                         database="metadatastore")
    try:
        script = "../resources/alter_table.sql"
        contents = open(script).read()
        print(contents)
        cursor = connection.cursor()
        for result in cursor.execute(contents, multi=True):
            print(result)

        for result in cursor.callproc("alter_reconciliation_table", ["ucfs", 5]):
            print(f"Result {result}")

    except mysql.connector.Error as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
