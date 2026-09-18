"""Floating recording indicator: a small rounded panel with a live waveform,
shown while recording. Pure AppKit on macOS, Tkinter on Windows/Linux."""
import collections
import sys
import threading

BAR_COUNT = 24
PANEL_W, PANEL_H = 260, 74
LABEL_H = 20  # bottom strip reserved for the "VoiceBud" label

IS_MACOS = sys.platform == "darwin"

if IS_MACOS:
    try:
        import objc
        from AppKit import (
            NSBackingStoreBuffered,
            NSBezierPath,
            NSColor,
            NSFont,
            NSFontAttributeName,
            NSForegroundColorAttributeName,
            NSMutableParagraphStyle,
            NSPanel,
            NSParagraphStyleAttributeName,
            NSScreen,
            NSTimer,
            NSView,
            NSWindowStyleMaskBorderless,
            NSWindowStyleMaskNonactivatingPanel,
        )
        from Foundation import NSString

        class WaveView(NSView):
            def initWithFrame_(self, frame):
                self = objc.super(WaveView, self).initWithFrame_(frame)
                if self is None:
                    return None
                self.levels = collections.deque([0.02] * BAR_COUNT, maxlen=BAR_COUNT)
                return self

            def drawRect_(self, rect):
                b = self.bounds()
                NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.92).setFill()
                NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(b, 16, 16).fill()
                pad, gap = 16, 3
                bw = (b.size.width - 2 * pad - gap * (BAR_COUNT - 1)) / BAR_COUNT
                wave_h = b.size.height - LABEL_H
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.64, 0.42, 1.0, 1.0).setFill()
                for i, lv in enumerate(self.levels):
                    bh = max(4, min(1.0, lv * 10) * (wave_h - 18))
                    x = pad + i * (bw + gap)
                    y = LABEL_H + (wave_h - bh) / 2
                    NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                        ((x, y), (bw, bh)), bw / 2, bw / 2
                    ).fill()
                style = NSMutableParagraphStyle.alloc().init()
                style.setAlignment_(1)  # center
                attrs = {
                    NSFontAttributeName: NSFont.boldSystemFontOfSize_(11),
                    NSForegroundColorAttributeName: NSColor.whiteColor(),
                    NSParagraphStyleAttributeName: style,
                }
                NSString.stringWithString_("VoiceBud").drawInRect_withAttributes_(
                    ((0, 4), (b.size.width, 14)), attrs
                )

        class MacOverlay:
            def __init__(self, level_fn):
                self.level_fn = level_fn
                screen = NSScreen.mainScreen().frame()
                x = (screen.size.width - PANEL_W) / 2
                self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
                    ((x, 110), (PANEL_W, PANEL_H)),
                    NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel,
                    NSBackingStoreBuffered,
                    False,
                )
                self.panel.setLevel_(25)
                self.panel.setOpaque_(False)
                self.panel.setBackgroundColor_(NSColor.clearColor())
                self.panel.setIgnoresMouseEvents_(True)
                self.panel.setCollectionBehavior_(1)
                self.view = WaveView.alloc().initWithFrame_(((0, 0), (PANEL_W, PANEL_H)))
                self.panel.setContentView_(self.view)
                self._timer = None

            def _tick(self, _timer):
                self.view.levels.append(self.level_fn())
                self.view.setNeedsDisplay_(True)

            def show(self):
                self.view.levels.extend([0.02] * BAR_COUNT)
                self.panel.orderFrontRegardless()
                self._timer = NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                    1 / 30.0, True, self._tick
                )

            def hide(self):
                if self._timer is not None:
                    self._timer.invalidate()
                    self._timer = None
                self.panel.orderOut_(None)

            def mainloop(self):
                pass

            def close(self):
                self.hide()

        HAS_APPKIT = True
    except ImportError:
        HAS_APPKIT = False
else:
    HAS_APPKIT = False


import tkinter as tk


class TkOverlay:
    """Floating recording pill for Windows / Linux with native rounded transparency."""

    def __init__(self, level_fn):
        self.level_fn = level_fn
        self.levels = collections.deque([0.02] * BAR_COUNT, maxlen=BAR_COUNT)
        self._timer = None
        self._is_showing = False

        self.root = tk.Tk()
        self.root.title("VoiceBud")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - PANEL_W) // 2
        y = screen_h - PANEL_H - 100
        self.root.geometry(f"{PANEL_W}x{PANEL_H}+{x}+{y}")

        self._bg_trans = "#010101"
        self._pill_color = "#101014"
        self._bar_color = "#a36bff"
        self.root.configure(bg=self._bg_trans)
        try:
            self.root.wm_attributes("-transparentcolor", self._bg_trans)
        except Exception:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=PANEL_W,
            height=PANEL_H,
            bg=self._bg_trans,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.root.withdraw()

    def _draw(self):
        self.canvas.delete("all")
        r = 16
        w, h = PANEL_W, PANEL_H
        d = 2 * r
        c = self._pill_color

        # Rounded rectangle background
        self.canvas.create_arc(0, 0, d, d, start=90, extent=90, fill=c, outline=c)
        self.canvas.create_arc(w - d, 0, w, d, start=0, extent=90, fill=c, outline=c)
        self.canvas.create_arc(0, h - d, d, h, start=180, extent=90, fill=c, outline=c)
        self.canvas.create_arc(w - d, h - d, w, h, start=270, extent=90, fill=c, outline=c)
        self.canvas.create_rectangle(r, 0, w - r, h, fill=c, outline=c)
        self.canvas.create_rectangle(0, r, w, h - r, fill=c, outline=c)

        # Purple waveform bars
        pad, gap = 16, 3
        bw = (w - 2 * pad - gap * (BAR_COUNT - 1)) / BAR_COUNT
        wave_h = h - LABEL_H
        for i, lv in enumerate(self.levels):
            bh = max(4.0, min(1.0, lv * 10) * (wave_h - 18))
            x = pad + i * (bw + gap) + bw / 2
            y_center = wave_h / 2
            half_len = max(1.0, (bh - bw) / 2)
            self.canvas.create_line(
                x, y_center - half_len, x, y_center + half_len,
                width=bw, capstyle=tk.ROUND, fill=self._bar_color
            )

        # "VoiceBud" label at bottom
        self.canvas.create_text(
            w / 2, h - 11,
            text="VoiceBud",
            fill="#ffffff",
            font=("Segoe UI", 9, "bold")
        )

    def _tick(self):
        if not self._is_showing:
            return
        self.levels.append(self.level_fn())
        self._draw()
        self._timer = self.root.after(33, self._tick)

    def _do_show(self):
        self._is_showing = True
        self.levels.clear()
        self.levels.extend([0.02] * BAR_COUNT)
        self._draw()
        self.root.deiconify()
        self.root.lift()
        self.root.wm_attributes("-topmost", True)
        if self._timer is not None:
            self.root.after_cancel(self._timer)
        self._timer = self.root.after(33, self._tick)

    def _do_hide(self):
        self._is_showing = False
        if self._timer is not None:
            self.root.after_cancel(self._timer)
            self._timer = None
        self.root.withdraw()

    def show(self):
        if threading.current_thread() is threading.main_thread():
            self._do_show()
        else:
            self.root.after(0, self._do_show)

    def hide(self):
        if threading.current_thread() is threading.main_thread():
            self._do_hide()
        else:
            self.root.after(0, self._do_hide)

    def mainloop(self):
        self.root.mainloop()

    def close(self):
        if threading.current_thread() is threading.main_thread():
            self._do_hide()
            self.root.destroy()
        else:
            self.root.after(0, self.close)


if HAS_APPKIT:
    Overlay = MacOverlay
else:
    Overlay = TkOverlay
