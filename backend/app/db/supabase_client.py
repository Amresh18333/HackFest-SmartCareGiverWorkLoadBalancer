"""
Supabase client module.

Uses real Supabase client when credentials are available (production).
Falls back to local JSON-based mock client for local development.
"""

import json
import os
import sys
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

# ============================================================
# CONFIGURATION
# ============================================================

TABLES = [
    "team_members",
    "teams",
    "tasks",
    "risk_signals",
    "risk_scores",
    "proposed_reassignments",
]

# ============================================================
# MOCK SUPABASE CLIENT (always defined)
# ============================================================

DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "mock_data",
)

os.makedirs(DATA_DIR, exist_ok=True)


class MockResult:
    """Simple result object that behaves similarly to Supabase responses."""

    def __init__(self, data: Any = None):
        self.data = data

    def execute(self) -> "MockResult":
        return self


class MockTable:
    """JSON-backed mock implementation of a Supabase table."""

    def __init__(self, name: str):
        self.name = name
        self.filepath = os.path.join(DATA_DIR, f"{name}.json")

        self.data: List[Dict[str, Any]] = self._load()

        self._query_filters: List[Any] = []
        self._order_by: Optional[tuple] = None
        self._limit: Optional[int] = None
        self._single: bool = False
        self._update_data: Optional[Dict[str, Any]] = None

    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------

    def _load(self) -> List[Dict[str, Any]]:
        """Load table data from JSON."""

        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

            return []

        except (json.JSONDecodeError, OSError):
            return []

    def _save(self) -> None:
        """Save table data to JSON."""

        os.makedirs(DATA_DIR, exist_ok=True)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                default=str,
                indent=2,
            )

    # --------------------------------------------------------
    # Query building
    # --------------------------------------------------------

    def select(self, columns: str = "*") -> "MockTable":
        """Start a SELECT query."""

        self._query_filters = []
        self._order_by = None
        self._limit = None
        self._single = False
        self._update_data = None

        return self

    def eq(self, field: str, value: Any) -> "MockTable":
        """Filter where field equals value."""

        self._query_filters.append(
            ("eq", field, value)
        )

        return self

    def neq(self, field: str, value: Any) -> "MockTable":
        """Filter where field does not equal value."""

        self._query_filters.append(
            ("neq", field, value)
        )

        return self

    def in_(self, field: str, values: List[Any]) -> "MockTable":
        """Filter where field is in a list."""

        self._query_filters.append(
            ("in", field, values)
        )

        return self

    def gte(self, field: str, value: Any) -> "MockTable":
        """Filter where field is greater than or equal to value."""

        self._query_filters.append(
            ("gte", field, value)
        )

        return self

    def lte(self, field: str, value: Any) -> "MockTable":
        """Filter where field is less than or equal to value."""

        self._query_filters.append(
            ("lte", field, value)
        )

        return self

    def gt(self, field: str, value: Any) -> "MockTable":
        """Filter where field is greater than value."""

        self._query_filters.append(
            ("gt", field, value)
        )

        return self

    def lt(self, field: str, value: Any) -> "MockTable":
        """Filter where field is less than value."""

        self._query_filters.append(
            ("lt", field, value)
        )

        return self

    def is_(
        self,
        field: str,
        value: Any,
    ) -> "MockTable":
        """Filter where field is NULL / TRUE / FALSE etc."""

        self._query_filters.append(
            ("is", field, value)
        )

        return self

    def or_(self, condition: str) -> "MockTable":
        """
        Basic OR filter support.

        Supports conditions such as:

            "name.eq.John,email.eq.test@example.com"
        """

        self._query_filters.append(
            ("or", condition)
        )

        return self

    def order(
        self,
        field: str,
        desc: bool = False,
    ) -> "MockTable":
        """Order query results."""

        self._order_by = (
            field,
            desc,
        )

        return self

    def limit(self, count: int) -> "MockTable":
        """Limit query results."""

        self._limit = count

        return self

    def single(self) -> "MockTable":
        """Return a single result."""

        self._single = True

        return self

    # --------------------------------------------------------
    # Query execution helpers
    # --------------------------------------------------------

    def _compare(
        self,
        actual: Any,
        operator: str,
        expected: Any,
    ) -> bool:
        """Safely compare values."""

        try:
            if operator == "eq":
                return actual == expected

            if operator == "neq":
                return actual != expected

            if operator == "gte":
                return actual >= expected

            if operator == "lte":
                return actual <= expected

            if operator == "gt":
                return actual > expected

            if operator == "lt":
                return actual < expected

            if operator == "is":
                return actual is expected

        except (TypeError, ValueError):
            return False

        return False

    def _apply_filters(
        self,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Apply all query filters."""

        result = items

        for filter_item in self._query_filters:
            filter_type = filter_item[0]

            # ------------------------------------------------
            # Equality
            # ------------------------------------------------

            if filter_type in {
                "eq",
                "neq",
                "gte",
                "lte",
                "gt",
                "lt",
                "is",
            }:
                _, field, value = filter_item

                result = [
                    item
                    for item in result
                    if self._compare(
                        item.get(field),
                        filter_type,
                        value,
                    )
                ]

            # ------------------------------------------------
            # IN
            # ------------------------------------------------

            elif filter_type == "in":
                _, field, values = filter_item

                result = [
                    item
                    for item in result
                    if item.get(field) in values
                ]

            # ------------------------------------------------
            # OR
            # ------------------------------------------------

            elif filter_type == "or":
                _, condition = filter_item

                parts = [
                    part.strip()
                    for part in condition.split(",")
                    if part.strip()
                ]

                or_conditions = []

                for part in parts:
                    if ".eq." in part:
                        field, value = part.split(
                            ".eq.",
                            1,
                        )

                        or_conditions.append(
                            ("eq", field, value)
                        )

                    elif ".neq." in part:
                        field, value = part.split(
                            ".neq.",
                            1,
                        )

                        or_conditions.append(
                            ("neq", field, value)
                        )

                if or_conditions:
                    filtered = []

                    for item in result:
                        matches = any(
                            self._compare(
                                item.get(field),
                                operator,
                                value,
                            )
                            for operator, field, value
                            in or_conditions
                        )

                        if matches:
                            filtered.append(item)

                    result = filtered

        return result

    def _apply_order(
        self,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Apply ordering."""

        if not self._order_by:
            return items

        field, desc = self._order_by

        try:
            return sorted(
                items,
                key=lambda item: (
                    item.get(field)
                    if item.get(field) is not None
                    else ""
                ),
                reverse=desc,
            )

        except TypeError:
            return items

    def _apply_limit(
        self,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Apply result limit."""

        if self._limit is None:
            return items

        return items[: self._limit]

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    def execute(self) -> "MockResult":
        """Execute SELECT or UPDATE query."""

        # UPDATE
        if self._update_data is not None:
            return self._execute_update()

        # SELECT
        result = self._apply_filters(
            deepcopy(self.data)
        )

        result = self._apply_order(result)

        result = self._apply_limit(result)

        if self._single:
            return MockResult(
                result[0] if result else None
            )

        return MockResult(result)

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    def insert(
        self,
        data: Any,
    ) -> "MockResult":
        """Insert one or multiple rows."""

        items = (
            data
            if isinstance(data, list)
            else [data]
        )

        inserted = []

        for original_item in items:
            item = deepcopy(original_item)

            if "id" not in item:
                item["id"] = str(uuid.uuid4())

            if "created_at" not in item:
                item["created_at"] = (
                    datetime.now().isoformat()
                )

            self.data.append(item)
            inserted.append(item)

        self._save()

        return MockResult(inserted)

    # --------------------------------------------------------
    # UPSERT
    # --------------------------------------------------------

    def upsert(
        self,
        data: Any,
        on_conflict: Optional[str] = None,
    ) -> "MockResult":
        """Insert or update rows."""

        items = (
            data
            if isinstance(data, list)
            else [data]
        )

        conflict_fields = (
            on_conflict.split(",")
            if on_conflict
            else ["id"]
        )

        result_items = []

        for original_item in items:
            item = deepcopy(original_item)

            if "id" not in item:
                item["id"] = str(uuid.uuid4())

            now = datetime.now().isoformat()

            if "updated_at" not in item:
                item["updated_at"] = now

            existing_index = None

            for index, existing in enumerate(self.data):
                if all(
                    existing.get(field)
                    == item.get(field)
                    for field in conflict_fields
                ):
                    existing_index = index
                    break

            if existing_index is not None:
                self.data[existing_index].update(item)

                result_items.append(
                    self.data[existing_index]
                )

            else:
                self.data.append(item)
                result_items.append(item)

        self._save()

        return MockResult(result_items)

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        data: Dict[str, Any],
    ) -> "MockTable":
        """Prepare an UPDATE query."""

        self._update_data = deepcopy(data)

        return self

    def _execute_update(self) -> "MockResult":
        """Execute an UPDATE query."""

        filters = list(self._query_filters)

        updated = []

        for item in self.data:
            matches = True

            for filter_item in filters:
                filter_type = filter_item[0]

                # Basic update filtering
                if filter_type == "eq":
                    _, field, value = filter_item

                    if item.get(field) != value:
                        matches = False
                        break

                elif filter_type == "in":
                    _, field, values = filter_item

                    if item.get(field) not in values:
                        matches = False
                        break

            if matches:
                item.update(
                    deepcopy(
                        self._update_data
                    )
                )

                item["updated_at"] = (
                    datetime.now().isoformat()
                )

                updated.append(
                    deepcopy(item)
                )

        self._save()

        self._query_filters = []
        self._update_data = None

        return MockResult(updated)

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete(self) -> "MockTable":
        """Prepare a DELETE query."""

        self._delete_requested = True

        return self

    def _execute_delete(self) -> "MockResult":
        """Execute DELETE query."""

        filters = list(self._query_filters)

        deleted = []
        remaining = []

        for item in self.data:
            matches = True

            for filter_item in filters:
                filter_type = filter_item[0]

                if filter_type == "eq":
                    _, field, value = filter_item

                    if item.get(field) != value:
                        matches = False
                        break

                elif filter_type == "in":
                    _, field, values = filter_item

                    if item.get(field) not in values:
                        matches = False
                        break

            if matches:
                deleted.append(deepcopy(item))
            else:
                remaining.append(item)

        self.data = remaining
        self._save()

        self._query_filters = []

        return MockResult(deleted)


# ============================================================
# MOCK SUPABASE CLIENT
# ============================================================


class MockSupabaseClient:
    """Local JSON-backed replacement for Supabase."""

    def __init__(self):
        self.tables = {
            name: MockTable(name)
            for name in TABLES
        }

    def table(
        self,
        name: str,
    ) -> "MockTable":
        """Return a table client."""

        if name not in self.tables:
            self.tables[name] = MockTable(name)

        return self.tables[name]


# ============================================================
# REAL SUPABASE CLIENT
# ============================================================

_real_client_available = False

try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv(
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    SUPABASE_ANON_KEY = os.getenv(
        "SUPABASE_ANON_KEY"
    )

    if (
        SUPABASE_URL
        and SUPABASE_SERVICE_ROLE_KEY
    ):
        from supabase import Client, create_client

        _real_client_available = True

except Exception as e:
    print(
        f"Warning: Supabase client unavailable: {e}"
    )
    _real_client_available = False


# ============================================================
# CLIENT INITIALIZATION
# ============================================================

_supabase = None
_supabase_admin = None


# ============================================================
# GET SUPABASE CLIENT
# ============================================================


if _real_client_available:

    def get_supabase():
        """
        Get the regular Supabase client.

        Uses the anon key when available.
        Falls back to the service role key if anon key
        is not configured.
        """

        global _supabase

        if _supabase is None:

            # Load application settings if available.
            try:
                from app.config import settings

                supabase_url = settings.supabase_url

                anon_key = getattr(
                    settings,
                    "supabase_anon_key",
                    None,
                )

                service_key = getattr(
                    settings,
                    "supabase_service_role_key",
                    None,
                )

            except Exception:
                supabase_url = os.getenv(
                    "SUPABASE_URL"
                )

                anon_key = os.getenv(
                    "SUPABASE_ANON_KEY"
                )

                service_key = os.getenv(
                    "SUPABASE_SERVICE_ROLE_KEY"
                )

            key = anon_key or service_key

            if not supabase_url or not key:
                raise RuntimeError(
                    "Supabase credentials are missing."
                )

            _supabase = create_client(
                supabase_url,
                key,
            )

        return _supabase


    def get_supabase_admin():
        """
        Get the Supabase admin client.

        Uses the service-role key.
        """

        global _supabase_admin

        if _supabase_admin is None:

            try:
                from app.config import settings

                supabase_url = settings.supabase_url

                service_key = (
                    settings.supabase_service_role_key
                )

            except Exception:
                supabase_url = os.getenv(
                    "SUPABASE_URL"
                )

                service_key = os.getenv(
                    "SUPABASE_SERVICE_ROLE_KEY"
                )

            if not supabase_url or not service_key:
                raise RuntimeError(
                    "Supabase admin credentials are missing."
                )

            _supabase_admin = create_client(
                supabase_url,
                service_key,
            )

        return _supabase_admin


    print("[OK] Using REAL Supabase client")


else:

    _mock_client: Optional[
        MockSupabaseClient
    ] = None


    def get_supabase() -> MockSupabaseClient:
        """Get the local mock Supabase client."""

        global _mock_client

        if _mock_client is None:
            _mock_client = MockSupabaseClient()

        return _mock_client


    def get_supabase_admin() -> MockSupabaseClient:
        """Get the local mock admin client."""

        return get_supabase()


    print(
        "[WARN] Using MOCK Supabase client "
        "(local development)"
    )

# Required imports
import json
import os
import sys
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

# Load settings
from app.config import settings