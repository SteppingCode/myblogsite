CREATE TABLE IF NOT EXISTS post(
id INTEGER PRIMARY KEY,
title TEXT UNIQUE,
text TEXT,
time INTEGER
);

create table if not exists menu (
id integer primary key,
title text not null,
url text not null
);

create table if not exists user (
id integer primary key,
username text not null unique,
password text not null,
email text not null unique,
status text
);

create table if not exists profile (
id integer primary key,
nick text not null unique,
name text not null,
age integer not null,
about text not null,
login text not null unique
);

create table if not exists comments (
id integer primary key,
username text not null,
text text not null,
postid integer not null
);

create table if not exists todo (
id integer primary key,
text text not null,
time integer not null
);
