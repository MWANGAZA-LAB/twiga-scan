from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import hashlib
import json
from datetime import datetime

from .database import Base
from ..config import settings


class ShardManager:
    """Manages database sharding for high-throughput scenarios"""
    
    def __init__(self):
        self.shards: Dict[int, Any] = {}
        self.shard_count = getattr(settings, 'SHARD_COUNT', 4)
        self.current_shard = 0
        
        # Initialize shard connections
        self._initialize_shards()
    
    def _initialize_shards(self):
        """Initialize database shards"""
        base_url = settings.DATABASE_URL
        
        for i in range(self.shard_count):
            # Create shard-specific database URL
            if 'postgresql' in base_url:
                shard_url = f"{base_url}_shard_{i}"
            else:
                # For SQLite, create separate files
                shard_url = base_url.replace('.db', f'_shard_{i}.db')
            
            # Create engine with optimized settings
            engine = create_engine(
                shard_url,
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Create session factory
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            
            self.shards[i] = {
                'engine': engine,
                'session_factory': SessionLocal,
                'url': shard_url
            }
    
    def get_shard_for_user(self, user_id: int) -> int:
        """Get shard number for a specific user"""
        return user_id % self.shard_count
    
    def get_shard_for_content(self, content: str) -> int:
        """Get shard number based on content hash"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return int(content_hash, 16) % self.shard_count
    
    def get_session(self, shard_id: Optional[int] = None) -> Any:
        """Get database session for specific shard"""
        if shard_id is None:
            shard_id = self.current_shard
        
        if shard_id not in self.shards:
            raise ValueError(f"Invalid shard ID: {shard_id}")
        
        return self.shards[shard_id]['session_factory']()
    
    def get_engine(self, shard_id: int) -> Any:
        """Get database engine for specific shard"""
        if shard_id not in self.shards:
            raise ValueError(f"Invalid shard ID: {shard_id}")
        
        return self.shards[shard_id]['engine']
    
    def create_tables(self):
        """Create tables in all shards"""
        for shard_id in range(self.shard_count):
            engine = self.get_engine(shard_id)
            Base.metadata.create_all(bind=engine)
    
    def get_shard_stats(self) -> Dict[str, Any]:
        """Get statistics for all shards"""
        stats = {}
        
        for shard_id in range(self.shard_count):
            engine = self.get_engine(shard_id)
            
            try:
                with engine.connect() as conn:
                    # Get table sizes
                    result = conn.execute(text("""
                        SELECT 
                            schemaname,
                            tablename,
                            attname,
                            n_distinct,
                            correlation
                        FROM pg_stats 
                        WHERE schemaname = 'public'
                    """))
                    
                    table_stats = {}
                    for row in result:
                        table_name = row.tablename
                        if table_name not in table_stats:
                            table_stats[table_name] = []
                        table_stats[table_name].append({
                            'column': row.attname,
                            'distinct_values': row.n_distinct,
                            'correlation': row.correlation
                        })
                    
                    stats[f'shard_{shard_id}'] = {
                        'url': self.shards[shard_id]['url'],
                        'table_stats': table_stats,
                        'status': 'healthy'
                    }
                    
            except Exception as e:
                stats[f'shard_{shard_id}'] = {
                    'url': self.shards[shard_id]['url'],
                    'status': 'error',
                    'error': str(e)
                }
        
        return stats


class ReadReplicaManager:
    """Manages read replicas for load balancing"""
    
    def __init__(self):
        self.replicas: Dict[str, Any] = {}
        self.current_replica = 0
        
        # Initialize read replicas
        self._initialize_replicas()
    
    def _initialize_replicas(self):
        """Initialize read replica connections"""
        replica_urls = getattr(settings, 'READ_REPLICA_URLS', [])
        
        for i, url in enumerate(replica_urls):
            engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            
            self.replicas[f'replica_{i}'] = {
                'engine': engine,
                'session_factory': SessionLocal,
                'url': url,
                'last_used': datetime.utcnow()
            }
    
    def get_read_session(self) -> Any:
        """Get session from a read replica (round-robin)"""
        if not self.replicas:
            return None
        
        replica_keys = list(self.replicas.keys())
        replica_key = replica_keys[self.current_replica % len(replica_keys)]
        self.current_replica += 1
        
        replica = self.replicas[replica_key]
        replica['last_used'] = datetime.utcnow()
        
        return replica['session_factory']()
    
    def get_replica_stats(self) -> Dict[str, Any]:
        """Get statistics for all read replicas"""
        stats = {}
        
        for name, replica in self.replicas.items():
            try:
                with replica['engine'].connect() as conn:
                    # Test connection
                    conn.execute(text("SELECT 1"))
                    
                    stats[name] = {
                        'url': replica['url'],
                        'last_used': replica['last_used'].isoformat(),
                        'status': 'healthy'
                    }
                    
            except Exception as e:
                stats[name] = {
                    'url': replica['url'],
                    'last_used': replica['last_used'].isoformat(),
                    'status': 'error',
                    'error': str(e)
                }
        
        return stats


# Global instances
shard_manager = ShardManager()
replica_manager = ReadReplicaManager()


def get_sharded_session(user_id: Optional[int] = None, content: Optional[str] = None) -> Any:
    """Get database session for appropriate shard"""
    if user_id is not None:
        shard_id = shard_manager.get_shard_for_user(user_id)
    elif content is not None:
        shard_id = shard_manager.get_shard_for_content(content)
    else:
        shard_id = 0
    
    return shard_manager.get_session(shard_id)


def get_read_session() -> Any:
    """Get session from read replica for read operations"""
    return replica_manager.get_read_session() 