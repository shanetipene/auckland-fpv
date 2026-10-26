-- Community ratings and spot suggestions for the Auckland FPV site
CREATE TABLE IF NOT EXISTS ratings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  spot_id TEXT NOT NULL,
  seclusion REAL NOT NULL,
  quiet REAL NOT NULL,
  flying REAL NOT NULL,
  ip_hash TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ratings_spot ON ratings(spot_id);
CREATE INDEX IF NOT EXISTS idx_ratings_ip ON ratings(ip_hash, spot_id, created_at);

CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  region TEXT,
  lat REAL,
  lon REAL,
  maps_url TEXT,
  access TEXT,
  why TEXT,
  hazards TEXT,
  submitter TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  review_note TEXT,
  ip_hash TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status, created_at);
