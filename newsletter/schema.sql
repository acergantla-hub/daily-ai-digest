-- Newsletter subscribers table
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    subscribed_at TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER NOT NULL DEFAULT 1,
    unsubscribe_token TEXT NOT NULL
);

-- Newsletter send log (track what was sent and when)
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_slug TEXT NOT NULL,
    post_title TEXT NOT NULL,
    post_url TEXT NOT NULL,
    sent_at TEXT NOT NULL DEFAULT (datetime('now')),
    recipient_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
);

-- Index for fast email lookups
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);
