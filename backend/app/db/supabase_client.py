"""
Real Supabase client for production.
Uses the official supabase-py library.
"""
from supabase import create_client, Client
from app.config import settings

# Global instances
_supabase: Client = None
_supabase_admin: Client = None

def get_supabase() -> Client:
    """Get Supabase client with anon key (for client-side operations)."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _supabase

def get_supabase_admin() -> Client:
    """Get Supabase client with service role key (for admin operations)."""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _supabase_admin