CREATE TABLE IF NOT EXISTS photo(
id INTEGER PRIMARY KEY,
photo BLOB,
post TEXT UNIQUE,
filename TEXT
);