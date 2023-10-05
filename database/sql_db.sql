CREATE TABLE IF NOT EXISTS post(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
text TEXT,
photo BLOB,
time INTEGER
);

create table if not exists menu (
id integer primary key autoincrement,
title text not null,
url text not null
);

create table if not exists user (
id integer primary key autoincrement,
username text not null unique,
password text not null
);

create table if not exists unregmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);

create table if not exists profile (
id integer primary key autoincrement,
nick text not null unique,
name text not null,
age integer not null,
about text not null
);

create table if not exists adminmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);

create table if not exists comments (
id integer primary key autoincrement,
username text not null,
text text not null,
postid integer not null
);

create table if not exists todo (
id integer primary key autoincrement,
text text not null,
time integer not null
);

create table if not exists updates (
id integer primary key autoincrement,
title text not null,
text text not null,
photo text not null,
time integer not null
);

create table if not exists likes (
id integer primary key autoincrement,
like integer not null,
dislike integer not null,
updateid integer not null
);