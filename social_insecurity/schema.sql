-- --
-- Create tables
-- --

CREATE TABLE IF NOT EXISTS [Users] (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR UNIQUE NOT NULL,
  first_name VARCHAR NOT NULL,
  last_name VARCHAR NOT NULL,
  [password] VARCHAR NOT NULL,
  education VARCHAR DEFAULT 'Unknown',
  employment VARCHAR DEFAULT 'Unknown',
  music VARCHAR DEFAULT 'Unknown',
  movie VARCHAR DEFAULT 'Unknown',
  nationality VARCHAR DEFAULT 'Unknown',
  birthday DATE DEFAULT 'Unknown'
);

CREATE TABLE IF NOT EXISTS [Posts](
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  u_id INTEGER NOT NULL,
  content INTEGER,
  [image] VARCHAR,
  [creation_time] DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (u_id) REFERENCES [Users](id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS [Friends](
  u_id INTEGER NOT NULL REFERENCES Users,
  f_id INTEGER NOT NULL REFERENCES Users,
  PRIMARY KEY(u_id, f_id),
  FOREIGN KEY (u_id) REFERENCES [Users](id) ON DELETE CASCADE,
  FOREIGN KEY (f_id) REFERENCES [Users](id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS [Comments](
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  p_id INTEGER NOT NULL,
  u_id INTEGER NOT NULL,
  comment VARCHAR,
  [creation_time] DATETIME,
  FOREIGN KEY (p_id) REFERENCES Posts(id) ON DELETE CASCADE,
  FOREIGN KEY (u_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- --
-- Populate tables with test data
-- --

INSERT INTO Users (
  username,
  first_name,
  last_name,
  [password]
)
VALUES (
  'test',
  'Jane',
  'Doe',
  'password123'
);