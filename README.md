# workout-db
`exerceisedb-create.sql`  is the create script to create the database from scratch.  You can use that to determine the schema of the database


`exercisingdb-exrx-parser.py` is the script used to download the data from a website and inserts it into the database.  This only needs to be run if the site updates it's data.  The downloading takes a few hours as to not have ip blocked by website and the uploading to sqllite takes less than a minute.
