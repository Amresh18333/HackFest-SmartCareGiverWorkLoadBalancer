"""
Supabase client - uses real client on Render (Linux), mock on Windows local dev.
"""
import os
import sys
from typing import Optional
from app.config import settings

# Check if we're on Render (Linux) or local Windows
IS_RENDER = os.getenv("RENDER", "false").lower() == "true" or "render" in os.getenv("HOSTNAME", "").lower()
IS_WINDOWS = sys.platform.startswith("win")

# Try to import real client, fall back to mock if it fails
_real_client_available = False
if not IS_WINDOWS:
    try:
        from supabase import create_client, Client
        _real_client_available = True
    except Exception:
        _real_client_available = False

if _real_client_available and (IS_RENDER or not IS_WINDOWS):
    # Use real Supabase client (production on Render)
    from supabase import create_client, Client
    
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
else:
    # Use mock client (local Windows development)
    import json
    import uuid
    from datetime import date, datetime
    from typing import Dict, List, Optional, Any
    from copy import deepcopy
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mock_data")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    TABLES = [
        "team_members", "teams", "tasks", "risk_signals",
        "risk_scores", "proposed_reassignments"
    ]
    
    class MockTable:
        def __init__(self, name: str):
            self.name = name
            self.filepath = os.path.join(DATA_DIR, f"{name}.json")
            self.data = self._load()
            self._query_filters = []
            self._order_by = None
            self._limit = None
            self._single = False
        
        def _load(self) -> List[Dict]:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r") as f:
                    return json.load(f)
            return []
        
        def _save(self):
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, default=str, indent=2)
        
        def select(self, columns: str = "*"):
            self._query_filters = []
            self._order_by = None
            self._limit = None
            self._single = False
            return self
        
        def eq(self, field: str, value: Any):
            self._query_filters.append(("eq", field, value))
            return self
        
        def in_(self, field: str, values: List[Any]):
            self._query_filters.append(("in", field, values))
            return self
        
        def gte(self, field: str, value: Any):
            self._query_filters.append(("gte", field, value))
            return self
        
        def lte(self, field: str, value: Any):
            self._query_filters.append(("lte", field, value))
            return self
        
        def or_(self, condition: str):
            self._query_filters.append(("or", condition))
            return self
        
        def order(self, field: str, desc: bool = False):
            self._order_by = (field, desc)
            return self
        
        def limit(self, count: int):
            self._limit = count
            return self
        
        def single(self):
            self._single = True
            return self
        
        def _apply_filters(self, items: List[Dict]) -> List[Dict]:
            result = items
            for filter_item in self._query_filters:
                if filter_item[0] == "eq":
                    _, field, value = filter_item
                    result = [item for item in result if item.get(field) == value]
                elif filter_item[0] == "in":
                    _, field, values = filter_item
                    result = [item for item in result if item.get(field) in values]
                elif filter_item[0] == "gte":
                    _, field, value = filter_item
                    result = [item for item in result if item.get(field, "") >= value]
                elif filter_item[0] == "lte":
                    _, field, value = filter_item
                    result = [item for item in result if item.get(field, "") <= value]
                elif filter_item[0] == "or":
                    _, condition = filter_item
                    parts = condition.split(",")
                    or_conditions = []
                    for part in parts:
                        if ".eq." in part:
                            field, val = part.split(".eq.")
                            or_conditions.append((field, val))
                    if or_conditions:
                        result = [item for item in result 
                                 if any(item.get(f) == v for f, v in or_conditions)]
            return result
        
        def _apply_order(self, items: List[Dict]) -> List[Dict]:
            if self._order_by:
                field, desc = self._order_by
                items = sorted(items, key=lambda x: x.get(field, ""), reverse=desc)
            return items
        
        def _apply_limit(self, items: List[Dict]) -> List[Dict]:
            if self._limit:
                return items[:self._limit]
            return items
        
        def execute(self):
            result = self._apply_filters(deepcopy(self.data))
            result = self._apply_order(result)
            result = self._apply_limit(result)
            
            if self._single:
                return type('Result', (), {'data': result[0] if result else None})()
            return type('Result', (), {'data': result})()
        
        def insert(self, data: Dict):
            items = data if isinstance(data, list) else [data]
            for item in items:
                if "id" not in item:
                    item["id"] = str(uuid.uuid4())
                if "created_at" not in item:
                    item["created_at"] = datetime.now().isoformat()
            self.data.extend(items)
            self._save()
            class Result:
                def __init__(self, data):
                    self.data = data
                def execute(self):
                    return self
            return Result(items)
        
        def upsert(self, data: Dict, on_conflict: str = None):
            items = data if isinstance(data, list) else [data]
            conflict_fields = on_conflict.split(",") if on_conflict else ["id"]
            
            for item in items:
                if "id" not in item:
                    item["id"] = str(uuid.uuid4())
                item["updated_at"] = datetime.now().isoformat()
                
                existing_idx = None
                for i, existing in enumerate(self.data):
                    if all(existing.get(f) == item.get(f) for f in conflict_fields):
                        existing_idx = i
                        break
                
                if existing_idx is not None:
                    self.data[existing_idx].update(item)
                else:
                    self.data.append(item)
            
            self._save()
            class Result:
                def __init__(self, data):
                    self.data = data
                def execute(self):
                    return self
            return Result(items)
        
        def update(self, data: Dict):
            self._update_data = data
            return self
        
        def _execute_update(self):
            filters = self._query_filters
            self._query_filters = []
            updated = []
            for item in self.data:
                match = True
                for filter_item in filters:
                    if filter_item[0] == "eq":
                        _, field, value = filter_item
                        if item.get(field) != value:
                            match = False
                            break
                if match:
                    item.update(self._update_data)
                    item["updated_at"] = datetime.now().isoformat()
                    updated.append(item)
            self._save()
            class Result:
                def __init__(self, data):
                    self.data = data
                def execute(self):
                    return self
            return Result(updated)
        
        def execute(self):
            if hasattr(self, '_update_data'):
                return self._execute_update()
            
            result = self._apply_filters(deepcopy(self.data))
            result = self._apply_order(result)
            result = self._apply_limit(result)
            
            if self._single:
                return type('Result', (), {'data': result[0] if result else None})()
            return type('Result', (), {'data': result})()
    
    class MockSupabaseClient:
        def __init__(self):
            self.tables = {name: MockTable(name) for name in TABLES}
        
        def table(self, name: str) -> MockTable:
            if name not in self.tables:
                self.tables[name] = MockTable(name)
            return self.tables[name]
    
    _mock_client = None
    
    def get_supabase() -> MockSupabaseClient:
        global _mock_client
        if _mock_client is None:
            _mock_client = MockSupabaseClient()
        return _mock_client
    
    def get_supabase_admin() -> MockSupabaseClient:
        return get_supabase()

# Export the appropriate functions based on environment
# These are already defined above in the appropriate branch