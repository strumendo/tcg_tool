# Android App Troubleshooting Guide

This document covers common issues encountered when building and running the TCG Meta Android app, particularly on Samsung Galaxy Z Fold 6 and other foldable devices.

## Table of Contents

1. [App Crashes on Startup](#app-crashes-on-startup)
2. [Kivy Metrics Issues](#kivy-metrics-issues)
3. [Canvas Binding Errors](#canvas-binding-errors)
4. [Build Issues](#build-issues)
5. [Debugging with ADB](#debugging-with-adb)

---

## App Crashes on Startup

### Symptom
App opens briefly showing splash screen, then immediately closes.

### Diagnosis
Use ADB logcat to capture Python errors:

```bash
# Clear logs and start app
adb logcat -c && adb shell am start -n com.pokemon.tcgmeta/org.kivy.android.PythonActivity

# Wait a few seconds, then capture logs
adb logcat -d | grep "python" | tail -50
```

### Common Causes

1. **ZeroDivisionError in sp() function** - See [Kivy Metrics Issues](#kivy-metrics-issues)
2. **AttributeError in canvas bindings** - See [Canvas Binding Errors](#canvas-binding-errors)
3. **Missing dependencies** - Check buildozer.spec requirements
4. **Native crash (SIGABRT)** - Usually SDL2/threading issue, requires clean rebuild

---

## Kivy Metrics Issues

### Problem: `ZeroDivisionError: division by zero` in `sp(41)`

**Error Message:**
```
kivy.lang.builder.BuilderException: Parser: File ".../kivy/data/style.kv", line 491:
  active_norm_pos: max(0., min(1., (int(self.active) + self.touch_distance / sp(41))))
ZeroDivisionError: division by zero
```

**Cause:**
On some Android devices (especially Samsung foldables), `Metrics.density` is not initialized when Kivy widgets are created, causing `sp()` to return 0.

**Solution:**
Add metrics initialization at the very beginning of `main.py`, BEFORE any Kivy widget imports:

```python
import os
os.environ.setdefault('KIVY_METRICS_DENSITY', '1')
os.environ.setdefault('KIVY_METRICS_FONTSCALE', '1')
os.environ.setdefault('KIVY_DPI', '96')

from kivy.metrics import Metrics

def _ensure_metrics_density():
    """Ensure Metrics.density has a valid value."""
    try:
        current_density = Metrics.density
        if current_density is None or current_density <= 0:
            Metrics.reset_metrics()
    except Exception:
        pass

_ensure_metrics_density()
```

**Affected Widgets:**
- `Switch` widget (uses `sp(41)` in default style)
- Any widget using `sp()` or `dp()` during initialization

---

## Canvas Binding Errors

### Problem: `AttributeError: 'BindTexture' object has no attribute 'pos'`

**Error Message:**
```
AttributeError: 'kivy.graphics.context_instructions.BindTexture' object has no attribute 'pos'
and no __dict__ for setting new attributes
```

**Cause:**
When accessing canvas instructions by index (e.g., `canvas.children[1]`), the order of instructions can vary. `BindTexture` is a context instruction that may appear before your `Rectangle` or `Ellipse`.

**Bad Pattern:**
```python
# DON'T DO THIS - canvas.children order is unreliable
with widget.canvas:
    Color(1, 1, 1, 1)
    Rectangle(pos=widget.pos, size=widget.size)
widget.bind(pos=lambda w, p: setattr(w.canvas.children[1], 'pos', p))  # May fail!
```

**Good Pattern:**
```python
# DO THIS - store direct reference to the instruction
with widget.canvas:
    Color(1, 1, 1, 1)
    widget._rect = Rectangle(pos=widget.pos, size=widget.size)
widget.bind(pos=lambda w, p: setattr(w._rect, 'pos', p) if hasattr(w, '_rect') else None)
widget.bind(size=lambda w, s: setattr(w._rect, 'size', s) if hasattr(w, '_rect') else None)
```

**For Ellipse (avatar circles):**
```python
with avatar.canvas.before:
    Color(*get_color_from_hex(COLORS['border']))
    avatar._ellipse = Ellipse(pos=avatar.pos, size=avatar.size)
avatar.bind(pos=lambda w, p: setattr(w._ellipse, 'pos', p) if hasattr(w, '_ellipse') else None)
avatar.bind(size=lambda w, s: setattr(w._ellipse, 'size', s) if hasattr(w, '_ellipse') else None)
```

---

## Build Issues

### Clean Rebuild

When experiencing unexplained native crashes, perform a clean rebuild:

```bash
cd android_app
source venv/bin/activate

# Clean build artifacts
buildozer android clean
rm -rf .buildozer/android/platform/build-*

# Rebuild
buildozer android debug
```

### NDK/SDK Version Warnings

**Warning:**
```
Maximum recommended NDK version is 28c, but newer versions may work.
```

This warning is usually safe to ignore. The app should still build and run correctly.

### Java Version

Ensure Java 17 is installed:
```bash
java -version  # Should show version 17.x
```

### Python Version

Use Python 3.10 or 3.11. Python 3.12+ may have `distutils` issues:
```bash
python --version  # Should be 3.10.x or 3.11.x
```

---

## Debugging with ADB

### Setup

1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect device via USB

### Verify Connection

```bash
adb devices -l
# Should show your device, e.g.:
# RQCX7005ZFB    device usb:1-5 product:q6qxxx model:SM_F956B
```

### Install APK

```bash
adb install -r bin/tcgmeta-2.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Start App and Capture Logs

```bash
# Clear old logs
adb logcat -c

# Start the app
adb shell am start -n com.pokemon.tcgmeta/org.kivy.android.PythonActivity

# Wait for app to start/crash, then capture logs
adb logcat -d | grep "python" | tail -100
```

### Check if App is Running

```bash
adb shell "ps -A | grep tcgmeta"
# If running, shows: u0_aXXX  PID  ... com.pokemon.tcgmeta
```

### Real-time Log Monitoring

```bash
# Monitor all Python logs in real-time
adb logcat -v time | grep -i python

# Monitor errors and crashes
adb logcat -v time | grep -iE "(fatal|signal|python|traceback|error)"
```

### Common Log Patterns

| Pattern | Meaning |
|---------|---------|
| `[INFO] [Base] Start application main loop` | App started successfully |
| `[INFO] [Base] Leaving application in progress...` | App is closing (check for traceback after) |
| `Python for android ended.` | Python interpreter stopped |
| `FORTIFY: pthread_mutex_lock called on a destroyed mutex` | Native threading crash |
| `Fatal signal 6 (SIGABRT)` | Native crash, needs clean rebuild |

---

## Samsung Galaxy Z Fold 6 Specific Issues

### Screen Mode Detection

The app supports both Cover Screen (folded) and Main Screen (unfolded) modes. Issues may occur during fold/unfold transitions.

**Solution:** The `ResponsiveManager` in `utils/responsive.py` handles mode detection with safe defaults:

```python
def _detect_mode(self, *args):
    # Safely get window dimensions
    try:
        width = Window.width or 800
        height = Window.height or 600
    except Exception:
        width, height = 800, 600

    # Safe density retrieval
    density = 1.0
    try:
        density = getattr(Window, 'density', None)
        if density is None or density <= 0:
            density = getattr(Metrics, 'density', 1.0) or 1.0
    except Exception:
        density = 1.0
```

### Aspect Ratio Breakpoints

| Mode | Aspect Ratio | Width (dp) |
|------|-------------|------------|
| Cover | >= 2.5 | < 400 |
| Main | < 1.5 | >= 600 |
| Phone | Other | < 600 |
| Tablet | Other | >= 800 |

---

## Quick Reference

### Startup Checklist

1. Device connected: `adb devices`
2. Install APK: `adb install -r bin/*.apk`
3. Clear logs: `adb logcat -c`
4. Start app: `adb shell am start -n com.pokemon.tcgmeta/org.kivy.android.PythonActivity`
5. Check status: `adb shell "ps -A | grep tcgmeta"`
6. Get logs: `adb logcat -d | grep python`

### Files to Check When Debugging

| File | Purpose |
|------|---------|
| `main.py` | Main app entry point, widget definitions |
| `utils/responsive.py` | Screen mode detection, metrics handling |
| `buildozer.spec` | Build configuration, dependencies |
| `.buildozer/android/platform/build-*/` | Build cache (delete for clean rebuild) |

---

## Contact

For issues not covered here, check:
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Project Issues](https://github.com/strumendo/tcg-tool/issues)
