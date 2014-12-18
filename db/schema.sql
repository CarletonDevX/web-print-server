DROP TABLE if exists entries;
CREATE TABLE Entries (
  id integer primary key autoincrement,
  time text not null,
  text text not null
);