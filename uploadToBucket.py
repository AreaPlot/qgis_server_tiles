import os
import boto3
from botocore.exceptions import ClientError
from utils.convert_path import convertPath
import sqlite3
import logging
import traceback
import sys

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def walk_tree(starting_point, database_file):
    path = starting_point
    if not os.path.exists(database_file):
        initialize_db(database_file)
    db = sqlite3.connect(database_file)
    cur = db.cursor()
    for root, dirs, files in os.walk(starting_point):
        data = []
        for file in files:
            file = os.path.join(root, file)
            converted_path = convertPath(file, path_type="mp")
            file_size = os.path.getsize(file)
            data.append((file, converted_path, file_size))
        if len(data):
            cur.executemany(
                "INSERT INTO upload_log (source_path, upload_path, file_size) VALUES (?,?,?)",
                data,
            )
            db.commit()
            logging.info(f"{len(data)} added...")


def process_upload_queue(database_file, file_size=0):
    db = sqlite3.connect(database_file)
    cur = db.cursor()
    remaining_sql = (
        "select count(*) from upload_log where file_size > ? and upload_date is null"
    )
    cur.execute(remaining_sql, (file_size,))
    remaining = cur.fetchone()[0]

    queue_sql = "select source_path, upload_path from upload_log where file_size > ? and upload_date is null limit 1000"
    update_sql_template = "update upload_log set upload_date = current_timestamp where source_path in ({}) and upload_date is null"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS"],
        aws_secret_access_key=os.environ["AWS_SECRET"],
    )

    while remaining:
        cur.execute(queue_sql, (file_size,))
        queue = cur.fetchall()

        try:
            update_records = []
            for item in queue:
                s3_client.upload_file(
                    item[0],
                    os.environ["AWS_BUCKET"],
                    item[1],
                    ExtraArgs={"ContentType": "image/png"},
                )
                update_records.append(item[0])
            questionmarks = "?" * len(update_records)
            update_sql = update_sql_template.format(",".join(questionmarks))
            cur.execute(update_sql, update_records)
        except Exception:
            logging.error(traceback.format_exc())
            sys.exit(2)

        cur.execute(remaining_sql, (file_size,))
        remaining = cur.fetchone()[0]
        db.commit()
        logging.info(f"{remaining} records remaining.")


def initialize_db(filename=":memory:"):
    db = sqlite3.connect(filename)
    cur = db.cursor()
    cur.execute(
        """CREATE TABLE upload_log (
    source_path TEXT,
    upload_path TEXT,
    file_size INTEGER,
    file_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_date TIMESTAMP DEFAULT NULL
)
    """
    )
    db.commit()


if __name__ == "__main__":
    from dotenv import load_dotenv
    import argparse

    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="uploadToBucket",
        description="Upload to S3, translating paths.",
        epilog="Prior to uploading, configure the .env file.",
    )
    parser.add_argument("database", help="Database file for tracking file uploads.")
    parser.add_argument(
        "-p", "--path", help="Starting path for directory of files to upload."
    )
    parser.add_argument("-o", "--overwrite", help="Overwrite the database file.")
    parser.add_argument(
        "-u",
        "--upload",
        help="Upload using the logging database specified.",
        action="store_true",
    )
    parser.add_argument(
        "-s", "--size", help="Upload files over the specified size (bytes)."
    )

    args = parser.parse_args()
    if args.overwrite:
        os.remove(args.database)
    if not os.path.exists(args.database):
        initialize_db(args.database)
    if args.path:
        walk_tree(starting_point=args.path, database_file=args.database)
    if args.upload:
        required_values = ("AWS_ACCESS", "AWS_SECRET", "AWS_BUCKET")
        if any(map(lambda x: x in os.environ, required_values)):
            process_upload_queue(args.database, args.size)
        else:
            logging.error("AWS configuration values not found. Exiting.")
