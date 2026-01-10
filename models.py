"""
Database models for Poetry Foundation Scraper using SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, event, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class Poet(Base):
    """Poet model - stores poet information"""
    __tablename__ = 'poets'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)

    # Relationship to poems
    poems = relationship('Poem', back_populates='poet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Poet(name='{self.name}')>"

    def __str__(self):
        return self.name


class Poem(Base):
    """Poem model - stores poem information"""
    __tablename__ = 'poems'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    poet_id = Column(Integer, ForeignKey('poets.id'), nullable=False)
    date_added = Column(DateTime, default=datetime.utcnow)

    # Relationship to poet
    poet = relationship('Poet', back_populates='poems')

    def __repr__(self):
        return f"<Poem(title='{self.title}', poet='{self.poet.name if self.poet else 'Unknown'}')>"

    def __str__(self):
        return f"{self.title} by {self.poet.name if self.poet else 'Unknown'}"


class DatabaseManager:
    """
    Database manager using SQLAlchemy ORM with FTS5 support

    This class provides an ORM-based interface while still supporting
    full-text search via SQLite's FTS5 extension.
    """

    def __init__(self, db_path="poems.db"):
        """Initialize database connection and create schema"""
        self.db_path = db_path

        # Create engine with appropriate settings
        if db_path == ":memory:":
            # For testing/in-memory database
            self.engine = create_engine(
                f'sqlite:///{db_path}',
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(f'sqlite:///{db_path}')

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

        # Set up FTS5 virtual table
        self._init_fts5()

    def _init_fts5(self):
        """Initialize FTS5 virtual table and triggers for full-text search"""
        with self.engine.connect() as conn:
            # Create FTS5 virtual table
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS poems_fts USING fts5(
                    title,
                    content,
                    poet_name,
                    content='poems',
                    content_rowid='id'
                )
            """))

            # Trigger to keep FTS5 in sync when poems are inserted
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS poems_ai AFTER INSERT ON poems BEGIN
                    INSERT INTO poems_fts(rowid, title, content, poet_name)
                    SELECT new.id, new.title, new.content, poets.name
                    FROM poets WHERE poets.id = new.poet_id;
                END
            """))

            # Trigger to keep FTS5 in sync when poems are deleted
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS poems_ad AFTER DELETE ON poems BEGIN
                    DELETE FROM poems_fts WHERE rowid = old.id;
                END
            """))

            # Trigger to keep FTS5 in sync when poems are updated
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS poems_au AFTER UPDATE ON poems BEGIN
                    DELETE FROM poems_fts WHERE rowid = old.id;
                    INSERT INTO poems_fts(rowid, title, content, poet_name)
                    SELECT new.id, new.title, new.content, poets.name
                    FROM poets WHERE poets.id = new.poet_id;
                END
            """))

            conn.commit()

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def add_poem(self, title, poet_name, content):
        """
        Add a poem to the database (ORM style)

        Args:
            title: Poem title
            poet_name: Poet's name
            content: Poem content/text

        Returns:
            Poem: The created or updated Poem object
        """
        session = self.get_session()
        try:
            # Get or create poet using ORM
            poet = session.query(Poet).filter_by(name=poet_name).first()
            if not poet:
                poet = Poet(name=poet_name)
                session.add(poet)
                session.flush()  # Get the poet ID

            # Check if poem already exists
            existing_poem = session.query(Poem).filter_by(
                title=title,
                poet_id=poet.id
            ).first()

            if existing_poem:
                # Update existing poem
                existing_poem.content = content
                existing_poem.date_added = datetime.utcnow()
                poem = existing_poem
            else:
                # Create new poem
                poem = Poem(title=title, content=content, poet=poet)
                session.add(poem)

            session.commit()
            return poem
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def search_poems(self, title="", poet_name=""):
        """
        Search for poems by title and/or poet name (ORM style)

        Args:
            title: Title to search for (case-insensitive partial match)
            poet_name: Poet name to search for (case-insensitive partial match)

        Returns:
            dict: {'title': str, 'poet': str, 'content': str, 'date_added': datetime} or None
        """
        session = self.get_session()
        try:
            query = session.query(Poem).join(Poet)

            if title:
                query = query.filter(Poem.title.ilike(f'%{title}%'))

            if poet_name:
                query = query.filter(Poet.name.ilike(f'%{poet_name}%'))

            poem = query.first()
            if poem:
                # Return a dictionary to avoid detached instance issues
                return {
                    'title': poem.title,
                    'poet': poem.poet.name,
                    'content': poem.content,
                    'date_added': poem.date_added
                }
            return None
        finally:
            session.close()

    def search_full_text(self, search_term, limit=50):
        """
        Full-text search in poem titles and content using FTS5

        Args:
            search_term: Search query (supports FTS5 syntax)
            limit: Maximum number of results

        Returns:
            List of tuples: (poem_id, title, poet_name, content, rank)

        FTS5 Query Examples:
            - Simple: "love"
            - AND: "love AND heart"
            - OR: "love OR heart"
            - Phrase: '"shall i compare thee"'
            - Proximity: 'NEAR(love death, 5)'
        """
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    p.id,
                    p.title,
                    po.name as poet_name,
                    p.content,
                    poems_fts.rank
                FROM poems_fts
                JOIN poems p ON poems_fts.rowid = p.id
                JOIN poets po ON p.poet_id = po.id
                WHERE poems_fts MATCH :search_term
                ORDER BY rank
                LIMIT :limit
            """), {"search_term": search_term, "limit": limit})
            return result.fetchall()

    def get_all_poets(self):
        """
        Get all poets with poem counts (ORM style)

        Returns:
            List of tuples: (poet_name, poem_count)
        """
        session = self.get_session()
        try:
            poets = session.query(Poet).all()
            return [(poet.name, len(poet.poems)) for poet in poets]
        finally:
            session.close()

    def get_poems_by_poet(self, poet_name):
        """
        Get all poems by a specific poet (ORM style)

        Args:
            poet_name: Poet name (case-insensitive partial match)

        Returns:
            List of dicts: [{'title': str, 'poet': str, 'content': str, 'date_added': datetime}]
        """
        session = self.get_session()
        try:
            poet = session.query(Poet).filter(
                Poet.name.ilike(f'%{poet_name}%')
            ).first()

            if poet:
                # Convert to list of dicts to avoid detached instance issues
                return [
                    {
                        'title': poem.title,
                        'poet': poet.name,
                        'content': poem.content,
                        'date_added': poem.date_added
                    }
                    for poem in poet.poems
                ]
            return []
        finally:
            session.close()

    def get_random_poem(self):
        """
        Get a random poem (ORM style)

        Returns:
            dict: {'title': str, 'poet': str, 'content': str, 'date_added': datetime} or None
        """
        session = self.get_session()
        try:
            poem = session.query(Poem).order_by(func.random()).first()
            if poem:
                return {
                    'title': poem.title,
                    'poet': poem.poet.name,
                    'content': poem.content,
                    'date_added': poem.date_added
                }
            return None
        finally:
            session.close()

    def get_poem_count(self):
        """Get total number of poems"""
        session = self.get_session()
        try:
            return session.query(Poem).count()
        finally:
            session.close()

    def get_poet_count(self):
        """Get total number of poets"""
        session = self.get_session()
        try:
            return session.query(Poet).count()
        finally:
            session.close()

    def export_to_dict(self):
        """
        Export entire database to dictionary format (compatible with old JSON format)

        Returns:
            dict: {poet_name: {poem_title: poem_content}}
        """
        session = self.get_session()
        try:
            result = {}
            poets = session.query(Poet).all()
            for poet in poets:
                result[poet.name] = {
                    poem.title: poem.content for poem in poet.poems
                }
            return result
        finally:
            session.close()

    def get_poets_with_counts(self):
        """Get all poets with poem counts using a single grouped query."""
        session = self.get_session()
        try:
            rows = (
                session.query(Poet.name, func.count(Poem.id))
                .join(Poem, Poem.poet_id == Poet.id)
                .group_by(Poet.id)
                .order_by(Poet.name)
                .all()
            )
            return [(name, int(count)) for name, count in rows]
        finally:
            session.close()

    def get_poem_by_poet_and_title(self, poet_name: str, title: str):
        """Fetch a single poem by exact poet name and exact title."""
        session = self.get_session()
        try:
            poem = (
                session.query(Poem)
                .join(Poet)
                .filter(Poet.name == poet_name, Poem.title == title)
                .first()
            )
            if not poem:
                return None
            return {
                'title': poem.title,
                'poet': poem.poet.name,
                'content': poem.content,
                'date_added': poem.date_added
            }
        finally:
            session.close()

    def search_poem_titles(self, search_term: str, poet_name: str = "", limit: int = 200):
        """Search poem titles containing a term (and optionally by poet) in one DB query."""
        session = self.get_session()
        try:
            q = session.query(Poem.title, Poet.name).join(Poet)

            if poet_name:
                q = q.filter(Poet.name.ilike(f"%{poet_name}%"))

            if search_term:
                q = q.filter(Poem.title.ilike(f"%{search_term}%"))

            q = q.order_by(Poet.name, Poem.title).limit(limit)
            rows = q.all()
            return [{'title': t, 'poet': p} for (t, p) in rows]
        finally:
            session.close()
