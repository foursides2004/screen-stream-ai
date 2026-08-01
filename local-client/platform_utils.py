"""
Cross-platform window utilities.
Provides window listing and finding for Windows (pygetwindow) and macOS (pyobjc/Quartz).
"""

from __future__ import annotations

import sys
from typing import Optional

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"


def is_macos() -> bool:
    return IS_MACOS


def is_windows() -> bool:
    return IS_WINDOWS


def get_window_list() -> list[dict]:
    """Get list of visible windows with title and geometry.

    Returns a list of dicts with keys: title, left, top, width, height.
    """
    if IS_WINDOWS:
        return _get_windows_list()
    elif IS_MACOS:
        return _get_macos_list()
    return []


def find_window_by_title(title_substring: str) -> Optional[dict]:
    """Find a window by title substring (case-insensitive)."""
    title_lower = title_substring.lower()
    for win in get_window_list():
        if title_lower in win["title"].lower():
            return win
    return None


def _get_windows_list() -> list[dict]:
    """Windows: use pygetwindow."""
    try:
        import pygetwindow as gw
    except ImportError:
        print("[WARN] pygetwindow not available — window capture disabled")
        return []

    windows = []
    try:
        for win in gw.getAllWindows():
            if win.title and win.visible and win.width > 0 and win.height > 0:
                windows.append({
                    "title": win.title,
                    "left": win.left,
                    "top": win.top,
                    "width": win.width,
                    "height": win.height,
                })
    except Exception as e:
        print(f"[WARN] Failed to enumerate windows: {e}")
    return windows


def _get_macos_list() -> list[dict]:
    """macOS: use Quartz CGWindowList."""
    try:
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
        )
    except ImportError:
        print("[WARN] pyobjc-framework-Quartz not available — window capture disabled")
        print("[HINT] Install with: pip install pyobjc-framework-Quartz")
        return []

    windows = []
    try:
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for window in window_list:
            # Skip windows without a name or with zero size
            name = window.get("kCGWindowName", "")
            bounds = window.get("kCGWindowBounds", {})
            width = bounds.get("Width", 0)
            height = bounds.get("Height", 0)

            if not name or width == 0 or height == 0:
                continue

            # Skip windows from this app itself
            owner = window.get("kCGWindowOwnerName", "")
            if owner in ("Python", "python3", "Terminal"):
                continue

            windows.append({
                "title": name,
                "left": int(bounds.get("X", 0)),
                "top": int(bounds.get("Y", 0)),
                "width": int(width),
                "height": int(height),
            })
    except Exception as e:
        print(f"[WARN] Failed to enumerate macOS windows: {e}")
    return windows
