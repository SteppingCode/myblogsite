create table if not exists post (
id integer primary key autoincrement,
title text not null,
text text not null,
photo text not null,
time integer not null
);

create table if not exists menu (
id integer primary key autoincrement,
title text not null,
url text not null
);

create table if not exists user (
id integer primary key autoincrement,
username text not null,
password text not null
);

create table if not exists adminmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);
