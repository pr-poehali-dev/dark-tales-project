CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    avatar TEXT,
    bio TEXT,
    rating DECIMAL(2,1) DEFAULT 0.0,
    stories_count INTEGER DEFAULT 0,
    followers INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    content TEXT,
    author_id INTEGER REFERENCES authors(id),
    rating DECIMAL(2,1) DEFAULT 0.0,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    reading_time INTEGER DEFAULT 10,
    published_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS story_genres (
    id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES stories(id),
    genre VARCHAR(100) NOT NULL,
    UNIQUE(story_id, genre)
);

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES stories(id),
    user_id INTEGER NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES stories(id),
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(story_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_stories_author ON stories(author_id);
CREATE INDEX IF NOT EXISTS idx_stories_published ON stories(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_story_genres_story ON story_genres(story_id);
CREATE INDEX IF NOT EXISTS idx_comments_story ON comments(story_id);
CREATE INDEX IF NOT EXISTS idx_likes_story ON likes(story_id);