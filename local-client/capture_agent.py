#!/usr/bin/env python3
"""
Screen Stream AI - Local Capture Agent
Captures screen via hotkey or auto-interval and sends to Next.js API for AI analysis.
Supports full monitor capture, window capture, auto-capture intervals, and deduplication.
Works on Windows and macOS.
"""

import json
import base64
import time
import sys
import os
import signal
import threading
import asyncio
import argparse
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from difflib import SequenceMatcher

import requests
import websockets
from dotenv import load_dotenv
from mss import mss
from PIL import Image, ImageFilter
from pynput import keyboard
from pynput.keyboard import Key, Listener
from reviewer_databank import ReviewerDatabank
from parse_response import parse_qa_from_response
from openrouter_client import OpenRouterClient
from mock_responder import MockResponder
from lens_client import get_lens_client
from platform_utils import (
    IS_WINDOWS,
    IS_MACOS,
    get_window_list,
    find_window_by_title,
    get_window_client_rect,
)


class Config:
    """Configuration manager with validation."""

    # Platform-aware hotkey defaults
    if IS_MACOS:
        _DEFAULT_HOTKEYS = {
            "captureHotkey": "cmd+shift+s",
            "quitHotkey": "cmd+shift+q",
            "toggleAutoCaptureHotkey": "cmd+shift+a",
            "cycleModeHotkey": "cmd+shift+m",
        }
    else:
        _DEFAULT_HOTKEYS = {
            "captureHotkey": "ctrl+alt+s",
            "quitHotkey": "ctrl+alt+q",
            "toggleAutoCaptureHotkey": "ctrl+alt+a",
            "cycleModeHotkey": "ctrl+alt+m",
        }

    DEFAULTS = {
        "apiBaseUrl": "http://localhost:3000",
        "apiEndpoint": "/api/analyze",
        "secretKey": "",
        "domain": "",
        "monitorIndex": 1,
        "maxWidth": 1920,
        "imageQuality": 80,
        "imageFormat": "webp",
        "requestTimeout": 30,
        "retryAttempts": 3,
        "retryDelay": 1000,
        "captureInterval": 30,
        "autoCapture": True,
        "captureMode": "monitor",
        "targetWindowTitle": "",
        "deduplicationEnabled": False,
        "deduplicationThreshold": 0.95,
        "dashboardWsEndpoint": "/api/ws",
        # Gemini / mock settings
        "mock": False,
        "openrouterApiKey": "",
        "openrouterModel": "google/gemini-3.5-flash-lite",
        "openrouterBaseUrl": "https://openrouter.ai/api/v1",
        "ragEnabled": True,
        "ragTopN": 3,
        "lensEnabled": False,
        "syncToVercel": False,
        **_DEFAULT_HOTKEYS,
    }

    # Map env var names to config.json keys
    _ENV_MAP = {
        "OPENROUTER_API_KEY": "openrouterApiKey",
        "OPENROUTER_MODEL": "openrouterModel",
        "OPENROUTER_BASE_URL": "openrouterBaseUrl",
        "APP_SECRET_KEY": "secretKey",
        "API_BASE_URL": "apiBaseUrl",
        "MOCK": "mock",
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.DEFAULTS.copy()
        self.load()

    def load(self) -> None:
        # Load .env first (so env vars are available as fallback)
        load_dotenv()

        # Load config.json (takes priority over .env)
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                print(f"[CONFIG] Loaded from {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] Failed to load config: {e}, using defaults")
        else:
            self.save()
            print(f"[CONFIG] Created default config at {self.config_path}")

    def save(self) -> None:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"[ERROR] Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        # Check config.json first, then fall back to env vars
        value = self.config.get(key)
        if value is not None:
            return value

        # Check mapped env vars
        for env_var, config_key in self._ENV_MAP.items():
            if config_key == key:
                env_val = os.environ.get(env_var)
                if env_val is not None:
                    return env_val

        return default

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save()

    def validate(self) -> bool:
        if not self.get("secretKey"):
            print("[ERROR] secretKey not configured (set in config.json or APP_SECRET_KEY env var)")
            return False
        if self.get("secretKey") == "your_super_secret_key_here_min_32_chars":
            print("[ERROR] Please change the default secretKey in config.json")
            return False
        if self.get("captureMode") not in ("monitor", "window"):
            print("[ERROR] captureMode must be 'monitor' or 'window'")
            return False
        if not self.get("mock", False) and not self.get("openrouterApiKey"):
            print("[ERROR] openrouterApiKey not configured — required when mock=false (set in config.json or OPENROUTER_API_KEY env var)")
            return False
        return True


class ScreenCapture:
    """Handles screen capture with multi-monitor and window support."""

    def __init__(self, config: Config):
        self.config = config
        self.active_window_title: Optional[str] = None  # set at startup, not persisted
        self._sct = mss()  # Initial instance for monitor detection
        self.monitors = self._sct.monitors
        print(f"[CAPTURE] Detected {len(self.monitors) - 1} monitor(s)")

    def _get_sct(self):
        """Get a new mss instance for thread-safe capture."""
        return mss()

    def get_monitor_info(self) -> Dict[str, Any]:
        idx = self.config.get("monitorIndex", 1)
        if idx < 1 or idx >= len(self.monitors):
            print(f"[WARN] Monitor index {idx} out of range, using primary (1)")
            idx = 1
        monitor = self.monitors[idx]
        return {
            "index": idx,
            "left": monitor["left"],
            "top": monitor["top"],
            "width": monitor["width"],
            "height": monitor["height"],
        }

    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of available windows with titles and geometry."""
        return get_window_list()

    def select_window_interactive(self) -> Optional[Dict[str, Any]]:
        """Interactive window selection at startup."""
        windows = self.get_window_list()
        if not windows:
            print("[WARN] No windows available for selection")
            return None

        print("\n" + "=" * 60)
        print("SELECT WINDOW TO CAPTURE")
        print("=" * 60)
        print("Available windows (visible, non-zero size):")
        print("-" * 60)

        for i, w in enumerate(windows, 1):
            print(f"  [{i:2d}] {w['title'][:60]:60s} ({w['width']}x{w['height']})")

        print("-" * 60)
        print(f"  [ 0] Full Monitor Capture")
        print("-" * 60)

        while True:
            try:
                choice = input(f"\nSelect window [0-{len(windows)}]: ").strip()
                if not choice:
                    continue
                idx = int(choice)
                if idx == 0:
                    return None  # Monitor mode
                if 1 <= idx <= len(windows):
                    selected = windows[idx - 1]
                    print(f"\n[SELECTED] '{selected['title']}' ({selected['width']}x{selected['height']})")
                    return selected
                print(f"Please enter a number between 0 and {len(windows)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n[CANCELLED]")
                return None

    def find_window_by_title(self, title_substring: str) -> Optional[Dict[str, Any]]:
        """Find window by title substring (case-insensitive)."""
        return find_window_by_title(title_substring)

    def capture(self) -> Optional[Image.Image]:
        """Capture screenshot based on captureMode config."""
        mode = self.config.get("captureMode", "monitor")

        if mode == "window":
            return self._capture_window()
        else:
            return self._capture_monitor()

    def _capture_monitor(self) -> Optional[Image.Image]:
        """Capture full monitor by index."""
        try:
            monitor_info = self.get_monitor_info()
            monitor = {
                "left": monitor_info["left"],
                "top": monitor_info["top"],
                "width": monitor_info["width"],
                "height": monitor_info["height"],
            }

            sct = self._get_sct()
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            print(f"[CAPTURE] Captured {img.width}x{img.height} from monitor {monitor_info['index']}")
            return img

        except Exception as e:
            print(f"[ERROR] Monitor capture failed: {e}")
            return None

    def _capture_window(self) -> Optional[Image.Image]:
        """Capture specific window by title."""
        if not get_window_list():
            print("[ERROR] Window capture not available on this platform - falling back to monitor capture")
            return self._capture_monitor()

        target_title = self.active_window_title or ""
        if not target_title:
            print("[ERROR] No window selected - falling back to monitor capture")
            return self._capture_monitor()

        window = self.find_window_by_title(target_title)
        if not window:
            print(f"[ERROR] Window not found: '{target_title}' - falling back to monitor capture")
            return self._capture_monitor()

        try:
            # Try to get client area (excludes title bar + borders)
            client_rect = get_window_client_rect(target_title)

            if client_rect:
                cx, cy, cw, ch = client_rect
                monitor = {"left": cx, "top": cy, "width": cw, "height": ch}
                print(f"[CAPTURE] Using client area: {cw}x{ch} at ({cx},{cy})")
            else:
                # Fallback: full window rect
                monitor = {
                    "left": window["left"],
                    "top": window["top"],
                    "width": window["width"],
                    "height": window["height"],
                }
                print(f"[CAPTURE] Client rect unavailable, using full window: {window['width']}x{window['height']}")

            sct = self._get_sct()
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            # If we used full window rect, crop title bar as fallback
            if not client_rect:
                TITLE_BAR_HEIGHT = 35
                if img.height > TITLE_BAR_HEIGHT * 2:
                    img = img.crop((0, TITLE_BAR_HEIGHT, img.width, img.height))
                    print(f"[CAPTURE] Cropped {TITLE_BAR_HEIGHT}px title bar -> {img.width}x{img.height}")

            print(f"[CAPTURE] Captured {img.width}x{img.height} from window: '{window['title']}'")
            return img

        except Exception as e:
            print(f"[ERROR] Window capture failed: {e} - falling back to monitor")
            return self._capture_monitor()

    def downscale_if_needed(self, img: Image.Image) -> Image.Image:
        """Downscale image if width exceeds maxWidth using LANCZOS."""
        max_width = self.config.get("maxWidth", 1920)
        if img.width <= max_width:
            return img

        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        print(f"[CAPTURE] Downscaling {img.width}x{img.height} -> {max_width}x{new_height}")

        return img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    def compute_phash(self, img: Image.Image) -> str:
        """Compute perceptual hash (pHash) for image deduplication.
        Returns 16-char hex string. Similar images have similar hashes.
        """
        # Resize to 32x32 grayscale
        small = img.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
        pixels = list(small.getdata())
        # Compute DCT-like average hash (simplified)
        avg = sum(pixels) / len(pixels)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        # Convert to hex
        return hex(int(bits, 2))[2:].zfill(16)

    def is_duplicate_image(self, img: Image.Image) -> bool:
        """Check if image is similar to last captured image using pHash."""
        if not self.config.get("deduplicationEnabled", True):
            return False

        if not hasattr(self, '_last_phash'):
            return False

        threshold = self.config.get("deduplicationThreshold", 0.95)
        current_hash = self.compute_phash(img)

        # Calculate similarity (Hamming distance)
        last_hash = self._last_phash
        if len(current_hash) != len(last_hash):
            return False

        # Convert hex to binary for comparison
        h1 = bin(int(current_hash, 16))[2:].zfill(64)
        h2 = bin(int(last_hash, 16))[2:].zfill(64)
        distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
        similarity = 1 - (distance / 64)

        if similarity >= threshold:
            print(f"[DEDUP] Skipping - image similarity {similarity:.2%} >= {threshold:.0%}")
            return True

        return False

    def update_phash(self, img: Image.Image) -> None:
        """Store perceptual hash of current image for next comparison."""
        self._last_phash = self.compute_phash(img)

    def encode_image(self, img: Image.Image) -> Optional[str]:
        """Encode image to base64 data URL."""
        try:
            format_ = self.config.get("imageFormat", "webp").upper()
            quality = self.config.get("imageQuality", 80)

            buffer = BytesIO()
            if format_ == "WEBP":
                img.save(buffer, format="WEBP", quality=quality, method=6)
                mime = "image/webp"
            elif format_ in ("JPEG", "JPG"):
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(buffer, format="JPEG", quality=quality, optimize=True)
                mime = "image/jpeg"
            else:
                img.save(buffer, format="PNG", optimize=True)
                mime = "image/png"

            b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            data_url = f"data:{mime};base64,{b64}"
            size_kb = len(data_url) / 1024
            print(f"[CAPTURE] Encoded to {mime} ({size_kb:.1f} KB)")
            return data_url

        except Exception as e:
            print(f"[ERROR] Image encoding failed: {e}")
            return None


class APIClient:
    """Handles API communication with retry logic."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get("apiBaseUrl", "http://localhost:3000").rstrip('/')
        self.endpoint = config.get("apiEndpoint", "/api/analyze")
        self.secret_key = config.get("secretKey", "")
        self.timeout = config.get("requestTimeout", 30)
        self.max_retries = config.get("retryAttempts", 3)
        self.retry_delay = config.get("retryDelay", 1000) / 1000.0

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ScreenStreamAI-Client/1.0",
        })

    def send_analysis(self, image_data_url: str, domain: str = "") -> Tuple[bool, Optional[str]]:
        """Send image to API for analysis with retries."""
        url = f"{self.base_url}{self.endpoint}"
        payload = {
            "image": image_data_url,
            "secretKey": self.secret_key,
        }
        if domain:
            payload["domain"] = domain

        for attempt in range(self.max_retries):
            try:
                print(f"[API] Sending to {url} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    stream=True,
                )

                if response.status_code == 401:
                    print("[ERROR] Unauthorized: Invalid secret key")
                    return False, "Invalid secret key"

                if response.status_code != 200:
                    error_text = response.text[:500]
                    print(f"[ERROR] API returned {response.status_code}: {error_text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False, f"HTTP {response.status_code}"

                print("[API] Streaming response...")
                full_response = ""
                for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        sys.stdout.write(chunk)
                        sys.stdout.flush()

                print("\n[API] Response complete")
                return True, full_response

            except requests.exceptions.Timeout:
                print(f"[WARN] Request timeout (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError:
                print(f"[WARN] Connection error (attempt {attempt + 1})")
            except Exception as e:
                print(f"[ERROR] Request failed: {e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)

        return False, "Max retries exceeded"

    def submit_result(self, text: str) -> bool:
        """Send pre-computed analysis to Vercel for dashboard display."""
        url = f"{self.base_url}/api/submit"
        payload = {"text": text, "secretKey": self.secret_key}
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                print("[API] Result submitted to dashboard")
                return True
            print(f"[WARN] Submit failed: {response.status_code}")
            return False
        except Exception as e:
            print(f"[WARN] Submit error: {e}")
            return False


class HotkeyManager:
    """Manages global hotkey listeners."""

    def __init__(self, config: Config, callbacks: Dict[str, callable]):
        self.config = config
        self.callbacks = callbacks
        self.listener: Optional[Listener] = None
        self._current_keys = set()
        self._parse_all_hotkeys()

    def _parse_all_hotkeys(self) -> None:
        """Parse all configured hotkeys into key sets."""
        self.hotkeys = {}
        for name in ("captureHotkey", "quitHotkey", "toggleAutoCaptureHotkey", "cycleModeHotkey"):
            hotkey_str = self.config.get(name, "")
            self.hotkeys[name] = self._parse_hotkey(hotkey_str)
            print(f"[HOTKEY] {name}: {hotkey_str} -> {self.hotkeys[name]}")

    def _parse_hotkey(self, hotkey_str: str) -> set:
        """Parse hotkey string like 'ctrl+shift+s' into a set of Key objects."""
        keys = set()
        parts = hotkey_str.lower().split('+')
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(Key.ctrl_l)
                keys.add(Key.ctrl_r)
            elif part == 'shift':
                keys.add(Key.shift_l)
                keys.add(Key.shift_r)
            elif part == 'alt':
                keys.add(Key.alt_l)
                keys.add(Key.alt_r)
            elif part in ('cmd', 'win'):
                keys.add(Key.cmd_l)
                keys.add(Key.cmd_r)
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                try:
                    keys.add(getattr(Key, part))
                except AttributeError:
                    print(f"[WARN] Unknown key: {part}")
        return keys

    def _on_press(self, key):
        self._current_keys.add(key)
        for name, hotkey_keys in self.hotkeys.items():
            if self._check_hotkey(hotkey_keys):
                callback_name = name.replace("Hotkey", "").lower()
                if callback_name in self.callbacks:
                    print(f"\n[HOTKEY] {name} triggered")
                    self.callbacks[callback_name]()

    def _on_release(self, key):
        self._current_keys.discard(key)

    def _check_hotkey(self, hotkey_keys: set) -> bool:
        """Check if all keys in hotkey are currently pressed."""
        return all(k in self._current_keys for k in hotkey_keys)

    def start(self) -> None:
        print("[HOTKEY] Listener started")
        self.listener = Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()

    def stop(self) -> None:
        if self.listener:
            self.listener.stop()
            print("[HOTKEY] Listener stopped")


class CaptureAgent:
    """Main application class coordinating capture, API, and hotkeys."""

    def __init__(self):
        self.config = Config()
        self.capture = ScreenCapture(self.config)
        self.api = APIClient(self.config)
        self.databank = ReviewerDatabank()

        # Gemini client (used when mock=false)
        self.openrouter_client = OpenRouterClient(
            api_key=self.config.get("openrouterApiKey", ""),
            model=self.config.get("openrouterModel", "google/gemini-3.5-flash-lite"),
            base_url=self.config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1"),
        )

        # Mock responder (used when mock=true)
        self.mock_responder = MockResponder()

        # State
        self.running = True
        self.capture_in_progress = False
        self.auto_capture_running = False
        self.auto_capture_thread: Optional[threading.Thread] = None

        # Deduplication state
        self.last_prompt = ""
        self.last_response = ""

        # Setup callbacks
        self.callbacks = {
            "capture": self.handle_capture,
            "quit": self.handle_quit,
            "toggleautocapture": self.toggle_auto_capture,
            "cyclemode": self.cycle_capture_mode,
        }

        self.hotkeys = HotkeyManager(self.config, self.callbacks)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n[SIGNAL] Shutdown signal received")
        self.handle_quit()

    def sync_databank_to_vercel(self) -> None:
        """Sync all local databank entries to Vercel on startup."""
        entries = self.databank.get_all()
        if not entries:
            return

        print(f"[SYNC] Syncing {len(entries)} local entries to Vercel...")
        synced = 0
        for entry in entries:
            try:
                r = requests.post(
                    f"{self.api.base_url}/api/reviewer/entries",
                    json={
                        "question": entry.question,
                        "choices": entry.choices,
                        "correctAnswer": entry.correct_answer,
                        "domain": entry.domain,
                    },
                    timeout=5,
                )
                if r.status_code == 200:
                    synced += 1
            except Exception:
                pass
        print(f"[SYNC] Synced {synced}/{len(entries)} entries")

    @staticmethod
    def _strip_json_block(text: str) -> str:
        """Remove ```json ... ``` blocks from response text for clean dashboard display."""
        import re
        return re.sub(r'```json\s*\n.*?\n\s*```', '', text, flags=re.DOTALL).strip()

    def _is_duplicate_prompt(self, prompt: str) -> bool:
        """Check if prompt is similar to last prompt using SequenceMatcher."""
        if not self.config.get("deduplicationEnabled", True):
            return False

        if not self.last_prompt:
            return False

        threshold = self.config.get("deduplicationThreshold", 0.95)
        similarity = SequenceMatcher(None, self.last_prompt, prompt).ratio()

        #if similarity >= threshold:
        #    print(f"[DEDUP] Skipping - prompt similarity {similarity:.2%} >= {threshold:.0%}")
        #    return True
        return False

    def handle_capture(self) -> None:
        """Handle capture request (manual or auto)."""
        if self.capture_in_progress:
            print("[CAPTURE] Already in progress, skipping")
            return

        self.capture_in_progress = True
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self) -> None:
        """Worker thread for capture + analysis."""
        try:
            print("\n" + "=" * 50)
            print("[CAPTURE] Starting screen capture...")

            img = self.capture.capture()
            if not img:
                return

            img = self.capture.downscale_if_needed(img)

            # Perceptual hash deduplication
            if self.capture.is_duplicate_image(img):
                return

            data_url = self.capture.encode_image(img)
            if not data_url:
                return

            # Update perceptual hash for next comparison
            self.capture.update_phash(img)

            domain = self.config.get("domain", "")
            timeout = self.config.get("requestTimeout", 30)

            # Branch based on mode: mock → lens+text → image
            if self.config.get("mock", False):
                response = self.mock_responder.generate()
            elif self.config.get("lensEnabled", False):
                # Lens pipeline: OCR → text-only Gemini (no image tokens)
                response = self._analyze_with_lens(img, domain, timeout)
            else:
                response = self.openrouter_client.analyze(data_url, domain, timeout=timeout)

            if response:
                print(f"[CAPTURE] Response: {response[:200]}...")
                self.last_response = response

                # Parse structured Q&A and save to databank
                parsed = parse_qa_from_response(response)
                if parsed:
                    existing = self.databank.find(parsed["question"])
                    entry = self.databank.add(
                        parsed["question"],
                        parsed["choices"],
                        parsed["correctAnswer"],
                        domain,
                    )
                    if existing:
                        print(f"[REVIEWER] Known question — seen {entry.seen_count} times")
                    else:
                        print(f"[REVIEWER] New question saved to databank")

                    # Sync to backend for reviewer dashboard
                    if self.config.get("syncToVercel", False):
                        try:
                            requests.post(
                                f"{self.api.base_url}/api/reviewer/entries",
                                json={
                                    "question": parsed["question"],
                                    "choices": parsed["choices"],
                                    "correctAnswer": parsed["correctAnswer"],
                                    "domain": domain,
                                },
                                timeout=5,
                            )
                        except Exception as sync_err:
                            print(f"[WARN] Failed to sync to reviewer backend: {sync_err}")
                else:
                    print("[REVIEWER] No structured data in response")

                # Submit to Vercel for dashboard display (strip JSON block)
                dashboard_text = self._strip_json_block(response)
                self.api.submit_result(dashboard_text)
            else:
                print("[CAPTURE] No response")

        except Exception as e:
            print(f"[ERROR] Capture worker failed: {e}")
        finally:
            self.capture_in_progress = False
            print("=" * 50 + "\n")

    def _analyze_with_lens(self, img, domain: str, timeout: int) -> Optional[str]:
        """Lens pipeline: OCR screenshot → send text to Gemini (no image tokens).

        This is much cheaper than sending images to Gemini because:
        1. Google Lens OCR is free
        2. Text-only Gemini prompts use far fewer tokens than image prompts
        """
        import tempfile

        tmp_path = None
        try:
            # Save image to temp file for Lens
            from io import BytesIO
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(buf.read())
                tmp_path = f.name

            # Step 1: OCR with Google Lens (free)
            lens = get_lens_client()
            ocr_text = lens.ocr_from_path(tmp_path)

            if not ocr_text:
                print("[LENS] OCR returned no text, falling back to image analysis")
                data_url = self.capture.encode_image(img)
                return self.gemini_client.analyze(data_url, domain, timeout=timeout)

            print(f"[LENS] OCR extracted {len(ocr_text)} chars")
            print(f"[LENS] Text preview: {ocr_text[:200]}...")

            # Step 2: Send text to Gemini (text-only, no image)
            response = self.openrouter_client.analyze_text(ocr_text, domain, timeout=timeout)
            return response

        except Exception as e:
            print(f"[LENS] Pipeline error: {e}, falling back to image analysis")
            data_url = self.capture.encode_image(img)
            return self.gemini_client.analyze(data_url, domain, timeout=timeout)

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def toggle_auto_capture(self) -> None:
        """Toggle auto-capture on/off."""
        if self.auto_capture_running:
            self.stop_auto_capture()
        else:
            self.start_auto_capture()

    def start_auto_capture(self) -> None:
        """Start auto-capture background thread."""
        if self.auto_capture_running:
            print("[AUTO] Already running")
            return

        interval = self.config.get("captureInterval", 10)
        if interval < 1:
            print("[AUTO] Invalid interval")
            return

        self.auto_capture_running = True
        self.auto_capture_thread = threading.Thread(target=self._auto_capture_loop, daemon=True)
        self.auto_capture_thread.start()
        print(f"[AUTO] Started - capturing every {interval}s")

    def stop_auto_capture(self) -> None:
        """Stop auto-capture background thread."""
        if not self.auto_capture_running:
            print("[AUTO] Not running")
            return

        self.auto_capture_running = False
        if self.auto_capture_thread:
            self.auto_capture_thread.join(timeout=2)
        print("[AUTO] Stopped")

    def _auto_capture_loop(self) -> None:
        """Background loop for auto-capture."""
        while self.auto_capture_running and self.running:
            if not self.capture_in_progress:
                self.handle_capture()

            interval = self.config.get("captureInterval", 10)
            # Sleep in small increments to allow quick shutdown
            for _ in range(interval * 10):
                if not self.auto_capture_running or not self.running:
                    break
                time.sleep(0.1)

    def cycle_capture_mode(self) -> None:
        """Cycle through capture modes: monitor -> window -> monitor..."""
        current = self.config.get("captureMode", "monitor")
        new_mode = "window" if current == "monitor" else "monitor"
        self.config.set("captureMode", new_mode)

        if new_mode == "window":
            # Prompt for window selection
            if get_window_list():
                selected = self.capture.select_window_interactive()
                if selected:
                    self.capture.active_window_title = selected["title"]
                    print(f"[MODE] Switched to window: '{selected['title']}'")
                else:
                    # User chose monitor fallback
                    self.config.set("captureMode", "monitor")
                    print(f"[MODE] No window selected, staying on monitor")
            else:
                print("[MODE] Window capture not available, staying on monitor")
                self.config.set("captureMode", "monitor")
        else:
            self.capture.active_window_title = None
            monitor_idx = self.config.get("monitorIndex", 1)
            print(f"[MODE] Switched to monitor: {monitor_idx}")

    def handle_quit(self) -> None:
        """Handle quit request."""
        print("[AGENT] Shutting down...")
        self.running = False
        self.stop_auto_capture()
        self.hotkeys.stop()

    def run(self) -> None:
        """Main run loop."""
        if not self.config.validate():
            sys.exit(1)

        print("\n" + "=" * 50)
        print("SCREEN STREAM AI - Local Capture Agent")
        print("=" * 50)
        print(f"API: {self.config.get('apiBaseUrl')}{self.config.get('apiEndpoint')}")
        domain = self.config.get('domain', '')
        if domain:
            print(f"Domain: {domain}")
        print(f"Mode: {self.config.get('captureMode', 'monitor')}")

        # Interactive window selection at startup
        if get_window_list():
            selected_window = self.capture.select_window_interactive()
            if selected_window is None:
                # User chose monitor mode
                self.config.set("captureMode", "monitor")
                print(f"Monitor: {self.config.get('monitorIndex', 1)}")
            else:
                # User selected a window — store in memory only, not persisted
                self.config.set("captureMode", "window")
                self.capture.active_window_title = selected_window["title"]
                print(f"Target Window: '{selected_window['title']}'")
        else:
            print(f"Mode: {self.config.get('captureMode', 'monitor')}")
            if self.config.get("captureMode") == "monitor":
                print(f"Monitor: {self.config.get('monitorIndex', 1)}")

        print(f"Max Width: {self.config.get('maxWidth', 1920)}")
        print(f"Format: {self.config.get('imageFormat', 'webp')}")
        mock_enabled = self.config.get("mock", False)
        print(f"Mock Mode: {'ON (no Gemini tokens consumed)' if mock_enabled else 'OFF'}")
        if not mock_enabled:
            print(f"Model: {self.config.get('openrouterModel', 'google/gemini-3.1-flash-lite')}")
        print(f"Auto-Capture: {'ON' if self.config.get('autoCapture') else 'OFF'} "
              f"({self.config.get('captureInterval', 10)}s interval)")
        print(f"Deduplication: {'ON' if self.config.get('deduplicationEnabled') else 'OFF'} "
              f"(threshold: {self.config.get('deduplicationThreshold', 0.95):.0%})")
        print("-" * 50)

        # Show available windows if in window mode (for reference)
        if self.config.get("captureMode") == "window" and get_window_list():
            print("\nAvailable windows:")
            for w in self.capture.get_window_list():
                marker = " >>>" if self.capture.active_window_title and self.capture.active_window_title.lower() in w["title"].lower() else ""
                print(f"  '{w['title']}' ({w['width']}x{w['height']}){marker}")

        print("-" * 50)
        print("Hotkeys:")
        print(f"  {self.config.get('captureHotkey')} - Manual capture")
        print(f"  {self.config.get('toggleAutoCaptureHotkey')} - Toggle auto-capture")
        print(f"  {self.config.get('cycleModeHotkey')} - Cycle capture mode (monitor/window)")
        print(f"  {self.config.get('quitHotkey')} - Quit")
        print("=" * 50 + "\n")

        # Sync local databank to Vercel on startup
        if self.config.get("syncToVercel", False):
            self.sync_databank_to_vercel()
        else:
            print("[SYNC] syncToVercel=false, skipping Vercel sync")

        # Start auto-capture if enabled
        if self.config.get("autoCapture", True):
            self.start_auto_capture()

        self.hotkeys.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.handle_quit()

        print("[AGENT] Stopped")


def main():
    # Set DPI awareness so pygetwindow, GetClientRect, and mss use the same coordinates
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Screen Stream AI - Local Capture Agent")
    parser.add_argument("--domain", type=str, default="", help="Domain context for exam questions (e.g., SFCC, AWS)")
    args = parser.parse_args()

    agent = CaptureAgent()
    if args.domain:
        agent.config.set("domain", args.domain)
        print(f"[CONFIG] Domain set to: {args.domain}")
    agent.run()


if __name__ == "__main__":
    main()