from drf_yasg.inspectors import SwaggerAutoSchema


class CustomAutoSchema(SwaggerAutoSchema):
    """
    Robust AutoSchema that supports BOTH:
      - ViewSets (ModelViewSet, etc.)
      - GenericAPIView / APIView (ListCreateAPIView, RetrieveUpdateDestroyAPIView, etc.)

    It resolves summary/description via multiple possible keys because drf-yasg may
    generate operation_keys differently depending on the view type and routing.

    Priority:
      1) Respect @swagger_auto_schema overrides first
      2) Try multiple lookup keys (action/method/op_keys) and pick the first match
      3) Fallback to drf-yasg defaults
    """

    # -----------------------
    # Helpers
    # -----------------------
    def _get_override(self, name: str):
        """Return decorator override (if present) for the current operation."""
        return self.overrides.get(name)

    def _http_method(self) -> str:
        """Return lowercase HTTP method ('get', 'post', 'put', 'patch', 'delete')."""
        return (getattr(self, "method", "") or "").lower()

    def _operation_key_tail(self, operation_keys=None) -> str | None:
        """Return operation_keys[-1] if available (often 'list', 'retrieve', 'destroy', etc.)."""
        if operation_keys:
            return operation_keys[-1]
        return None

    def _generic_method_to_action_candidates(self) -> list[str]:
        """
        For GenericAPIView-derived classes, drf-yasg may conceptually map methods to actions.
        We provide candidates to match both styles:

        - ListCreateAPIView:
            GET  -> list
            POST -> create

        - RetrieveUpdateDestroyAPIView:
            GET    -> retrieve
            PUT    -> update
            PATCH  -> partial_update
            DELETE -> destroy
        """
        method = self._http_method()
        view_cls_name = self.view.__class__.__name__

        candidates = []

        # Common mappings
        if method == "get":
            candidates.append("retrieve")
            candidates.append("list")
        elif method == "post":
            candidates.append("create")
        elif method == "put":
            candidates.append("update")
        elif method == "patch":
            candidates.append("partial_update")
        elif method == "delete":
            candidates.append("destroy")

        # Optional: tighten based on known generic view class names
        # (keeps it flexible, but helps match the "right" one first)
        if "ListCreate" in view_cls_name and method == "get":
            candidates = ["list"] + [c for c in candidates if c != "list"]
        if "ListCreate" in view_cls_name and method == "post":
            candidates = ["create"] + [c for c in candidates if c != "create"]

        if "RetrieveUpdateDestroy" in view_cls_name and method == "get":
            candidates = ["retrieve"] + [c for c in candidates if c != "retrieve"]
        if "RetrieveUpdateDestroy" in view_cls_name and method == "put":
            candidates = ["update"] + [c for c in candidates if c != "update"]
        if "RetrieveUpdateDestroy" in view_cls_name and method == "patch":
            candidates = ["partial_update"] + [c for c in candidates if c != "partial_update"]
        if "RetrieveUpdateDestroy" in view_cls_name and method == "delete":
            candidates = ["destroy"] + [c for c in candidates if c != "destroy"]

        return candidates

    def _build_lookup_keys(self, operation_keys=None) -> list[str]:
        """
        Build a list of lookup keys to try in swagger_summary/swagger_description maps.

        We try multiple keys because:
          - ViewSets may expose `view.action`
          - Generic views may match either HTTP methods or action-like names
          - drf-yasg operation_keys may end with action-like name
        """
        keys: list[str] = []

        # 1) ViewSet action if present
        action = getattr(self.view, "action", None)
        if action:
            keys.append(action)

        # 2) HTTP method name
        method = self._http_method()
        if method:
            keys.append(method)

        # 3) GenericAPIView method->action candidates (list/retrieve/create/...)
        keys.extend(self._generic_method_to_action_candidates())

        # 4) operation_keys tail (often the action-like name)
        tail = self._operation_key_tail(operation_keys)
        if tail:
            keys.append(tail)

        # De-duplicate while preserving order
        seen = set()
        ordered = []
        for k in keys:
            if k and k not in seen:
                seen.add(k)
                ordered.append(k)
        return ordered

    # -----------------------
    # Tags
    # -----------------------
    def get_tags(self, operation_keys=None):
        """
        Tag resolution priority:
          1) @swagger_auto_schema(tags=[...])
          2) view.swagger_tags = [...]
          3) drf-yasg default fallback (operation_keys[0])
        """
        tags = self._get_override("tags")
        if tags:
            return tags

        tags = getattr(self.view, "swagger_tags", None)
        if tags:
            return tags

        if operation_keys:
            return [operation_keys[0]]

        return []

    # -----------------------
    # Operation (reliable hook)
    # -----------------------
    def get_operation(self, operation_keys=None):
        """
        Build the Operation via drf-yasg, then post-process it to inject summary/description.
        This is the most reliable hook across ViewSets and GenericAPIView.
        """
        operation = super().get_operation(operation_keys)

        # Respect decorator overrides if explicitly provided
        override_summary = self._get_override("operation_summary")
        override_description = self._get_override("operation_description")

        # Compute candidate keys for mapping lookup
        keys_to_try = self._build_lookup_keys(operation_keys=operation_keys)

        # ---- Summary ----
        if override_summary is not None:
            operation.summary = override_summary
        else:
            summary_map = getattr(self.view, "swagger_summary", {}) or {}
            for key in keys_to_try:
                if key in summary_map:
                    operation.summary = summary_map[key]
                    break

        # ---- Description ----
        if override_description is not None:
            operation.description = override_description
        else:
            desc_map = getattr(self.view, "swagger_description", {}) or {}
            for key in keys_to_try:
                if key in desc_map:
                    operation.description = desc_map[key]
                    break

        return operation
