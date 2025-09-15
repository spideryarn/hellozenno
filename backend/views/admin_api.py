from flask import Blueprint, jsonify, request, g
from peewee import JOIN, fn
from loguru import logger

from utils.auth_utils import api_auth_required, api_admin_required
from db_models import AuthUser, Profile


admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


@admin_api_bp.route("/whoami", methods=["GET"])
@api_auth_required
def whoami():
    """Return whether the current user is an admin.

    Response: { "is_admin": bool }
    """
    return jsonify({"is_admin": bool(getattr(g, "is_admin", False))}), 200


@admin_api_bp.route("/users", methods=["GET"])
@api_admin_required
def list_users():
    """List users with profile info for admin UI.

    Query params:
      - page: int (default 1)
      - page_size: int (default 50)
      - sortField: one of email|created_at|last_sign_in_at|admin_granted_at
      - sortDir: asc|desc (default desc for created_at)
    """
    # Parse and sanitize query params
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except Exception:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 50))
        if page_size < 1:
            page_size = 50
        if page_size > 200:
            page_size = 200
    except Exception:
        page_size = 50

    sort_field = request.args.get("sortField") or None
    sort_dir = (request.args.get("sortDir") or "").lower() or None

    # Build base query with explicit aliases so we can safely return dicts()
    query = AuthUser.select(
        AuthUser.id.alias("id"),
        AuthUser.email.alias("email"),
        AuthUser.created_at.alias("created_at"),
        AuthUser.last_sign_in_at.alias("last_sign_in_at"),
        Profile.admin_granted_at.alias("admin_granted_at"),
        Profile.target_language_code.alias("target_language_code"),
        Profile.created_at.alias("profile_created_at"),
        Profile.updated_at.alias("profile_updated_at"),
    ).join(
        Profile,
        JOIN.LEFT_OUTER,
        on=(Profile.user_id == AuthUser.id.cast("text")),
    )

    # Sorting map
    sort_map = {
        "email": AuthUser.email,
        "created_at": AuthUser.created_at,
        "last_sign_in_at": AuthUser.last_sign_in_at,
        "admin_granted_at": Profile.admin_granted_at,
    }
    if sort_field in sort_map:
        field = sort_map[sort_field]
        order = field.asc() if sort_dir == "asc" else field.desc()
        query = query.order_by(order)
    else:
        # Default sort: created_at desc (most recent first)
        query = query.order_by(AuthUser.created_at.desc())

    # Total before pagination
    try:
        total = query.count()
    except Exception as e:
        logger.error(f"Failed to count users: {e}")
        total = 0

    # Pagination
    rows = []
    try:
        for row in query.paginate(page, page_size).dicts():
            rows.append(
                {
                    "id": str(row.get("id")) if row.get("id") is not None else None,
                    "email": row.get("email"),
                    "created_at": (
                        row.get("created_at").isoformat()
                        if row.get("created_at")
                        else None
                    ),
                    "last_sign_in_at": (
                        row.get("last_sign_in_at").isoformat()
                        if row.get("last_sign_in_at")
                        else None
                    ),
                    "admin_granted_at": (
                        row.get("admin_granted_at").isoformat()
                        if row.get("admin_granted_at")
                        else None
                    ),
                    "target_language_code": row.get("target_language_code"),
                    "profile_created_at": (
                        row.get("profile_created_at").isoformat()
                        if row.get("profile_created_at")
                        else None
                    ),
                    "profile_updated_at": (
                        row.get("profile_updated_at").isoformat()
                        if row.get("profile_updated_at")
                        else None
                    ),
                }
            )
    except Exception as e:
        logger.error(f"Failed to fetch users page={page} size={page_size}: {e}")
        rows = []

    return jsonify({"rows": rows, "total": total}), 200
