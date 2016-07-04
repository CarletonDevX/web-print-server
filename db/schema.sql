DROP TABLE if exists entries;
CREATE TABLE Entries (
  id integer primary key autoincrement,
  time integer not null,
  printer text not null,
  copies integer not null,
  success integer not null
);