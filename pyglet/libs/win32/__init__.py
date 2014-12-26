import struct

import pyglet
from . import constants
from .types import *


IS64 = struct.calcsize("P") == 8

_debug_win32 = pyglet.options['debug_win32']

if _debug_win32:
    import traceback
    _GetLastError = windll.kernel32.GetLastError
    _SetLastError = windll.kernel32.SetLastError
    _FormatMessageA = windll.kernel32.FormatMessageA

    _log_win32 = open('debug_win32.log', 'w')

    def format_error(err):
        msg = create_string_buffer(256)
        _FormatMessageA(constants.FORMAT_MESSAGE_FROM_SYSTEM,
                        c_void_p(),
                        err,
                        0,
                        msg,
                        len(msg),
                        c_void_p())
        return msg.value

    class DebugLibrary:

        def __init__(self, lib):
            self.lib = lib

        def __getattr__(self, name):
            fn = getattr(self.lib, name)

            def f(*args):
                _SetLastError(0)
                result = fn(*args)
                err = _GetLastError()
                if err != 0:
                    for entry in traceback.format_list(traceback.extract_stack()[:-1]):
                        _log_win32.write(entry)
                    print(format_error(err), file=_log_win32)
                return result
            return f
else:
    DebugLibrary = lambda lib: lib


gdi32 = DebugLibrary(windll.gdi32)
kernel32 = DebugLibrary(windll.kernel32)
user32 = DebugLibrary(windll.user32)
shell32 = DebugLibrary(windll.shell32)

# gdi32
gdi32.AddFontMemResourceEx.restype = HANDLE
gdi32.AddFontMemResourceEx.argtypes = [PVOID, DWORD, PVOID, POINTER(DWORD)]
gdi32.ChoosePixelFormat.restype = c_int
gdi32.ChoosePixelFormat.argtypes = [HDC, POINTER(PIXELFORMATDESCRIPTOR)]
gdi32.CreateBitmap.restype = HBITMAP
gdi32.CreateBitmap.argtypes = [c_int, c_int, UINT, UINT, c_void_p]
gdi32.CreateCompatibleDC.restype = HDC
gdi32.CreateCompatibleDC.argtypes = [HDC]
gdi32.CreateDIBitmap.restype = HBITMAP
gdi32.CreateDIBitmap.argtypes = [
    HDC, POINTER(BITMAPINFOHEADER), DWORD, c_void_p, POINTER(BITMAPINFO), UINT]
gdi32.CreateDIBSection.restype = HBITMAP
gdi32.CreateDIBSection.argtypes = [
    HDC, c_void_p, UINT, c_void_p, HANDLE, DWORD]  # POINTER(BITMAPINFO)
gdi32.CreateFontIndirectA.restype = HFONT
gdi32.CreateFontIndirectA.argtypes = [POINTER(LOGFONT)]
gdi32.DeleteDC.restype = BOOL
gdi32.DeleteDC.argtypes = [HDC]
gdi32.DeleteObject.restype = BOOL
gdi32.DeleteObject.argtypes = [HGDIOBJ]
gdi32.DescribePixelFormat.restype = c_int
gdi32.DescribePixelFormat.argtypes = [
    HDC, c_int, UINT, POINTER(PIXELFORMATDESCRIPTOR)]

# workaround for win 64-bit, see issue #664
# HDC, LPLOGFONT, FONTENUMPROC, LPARAM
gdi32.EnumFontFamiliesExA.argtypes = [HDC, c_void_p, c_void_p, LPARAM, DWORD]
gdi32.EnumFontFamiliesExA.restype = c_void_p

gdi32.ExtTextOutA.restype = BOOL
gdi32.ExtTextOutA.argtypes = [
    HDC, c_int, c_int, UINT, LPRECT, c_char_p, UINT, POINTER(INT)]
gdi32.GdiFlush.restype = BOOL
gdi32.GdiFlush.argtypes = list()
gdi32.GetCharABCWidthsW.restype = BOOL
gdi32.GetCharABCWidthsW.argtypes = [HDC, UINT, UINT, POINTER(ABC)]
gdi32.GetCharWidth32W.restype = BOOL
gdi32.GetCharWidth32W.argtypes = [HDC, UINT, UINT, POINTER(INT)]
gdi32.GetStockObject.restype = HGDIOBJ
gdi32.GetStockObject.argtypes = [c_int]
gdi32.GetTextMetricsA.restype = BOOL
gdi32.GetTextMetricsA.argtypes = [HDC, POINTER(TEXTMETRIC)]
gdi32.SelectObject.restype = HGDIOBJ
gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]
gdi32.SetBkColor.restype = COLORREF
gdi32.SetBkColor.argtypes = [HDC, COLORREF]
gdi32.SetBkMode.restype = c_int
gdi32.SetBkMode.argtypes = [HDC, c_int]
gdi32.SetPixelFormat.restype = BOOL
gdi32.SetPixelFormat.argtypes = [HDC, c_int, POINTER(PIXELFORMATDESCRIPTOR)]
gdi32.SetTextColor.restype = COLORREF
gdi32.SetTextColor.argtypes = [HDC, COLORREF]

kernel32.CloseHandle.restype = BOOL
kernel32.CloseHandle.argtypes = [HANDLE]
kernel32.CreateEventW.restype = HANDLE
kernel32.CreateEventW.argtypes = [
    POINTER(SECURITY_ATTRIBUTES), BOOL, BOOL, c_wchar_p]
kernel32.CreateWaitableTimerA.restype = HANDLE
kernel32.CreateWaitableTimerA.argtypes = [
    POINTER(SECURITY_ATTRIBUTES), BOOL, c_char_p]
kernel32.GetCurrentThreadId.restype = DWORD
kernel32.GetCurrentThreadId.argtypes = list()
kernel32.GetModuleHandleW.restype = HMODULE
kernel32.GetModuleHandleW.argtypes = [c_wchar_p]
kernel32.GlobalAlloc.restype = HGLOBAL
kernel32.GlobalAlloc.argtypes = [UINT, c_size_t]
kernel32.GlobalLock.restype = LPVOID
kernel32.GlobalLock.argtypes = [HGLOBAL]
kernel32.GlobalUnlock.restype = BOOL
kernel32.GlobalUnlock.argtypes = [HGLOBAL]
kernel32.SetLastError.restype = DWORD
kernel32.SetLastError.argtypes = list()
kernel32.SetWaitableTimer.restype = BOOL
kernel32.SetWaitableTimer.argtypes = [
    HANDLE, POINTER(LARGE_INTEGER), LONG, LPVOID, LPVOID, BOOL]  # TIMERAPCPROC
kernel32.WaitForSingleObject.restype = DWORD
kernel32.WaitForSingleObject.argtypes = [HANDLE, DWORD]

user32.AdjustWindowRectEx.restype = BOOL
user32.AdjustWindowRectEx.argtypes = [LPRECT, DWORD, BOOL, DWORD]
user32.ChangeDisplaySettingsExW.restype = LONG
user32.ChangeDisplaySettingsExW.argtypes = [
    c_wchar_p, POINTER(DEVMODE), HWND, DWORD, LPVOID]
user32.ClientToScreen.restype = BOOL
user32.ClientToScreen.argtypes = [HWND, LPPOINT]
user32.ClipCursor.restype = BOOL
user32.ClipCursor.argtypes = [LPRECT]
user32.CreateIconIndirect.restype = HICON
user32.CreateIconIndirect.argtypes = [POINTER(ICONINFO)]
user32.CreateWindowExW.restype = HWND
user32.CreateWindowExW.argtypes = [
    DWORD, c_wchar_p, c_wchar_p, DWORD, c_int, c_int, c_int, c_int, HWND, HMENU, HINSTANCE, LPVOID]
user32.DefWindowProcW.restype = LRESULT
user32.DefWindowProcW.argtypes = [HWND, UINT, WPARAM, LPARAM]
user32.DestroyWindow.restype = BOOL
user32.DestroyWindow.argtypes = [HWND]
user32.DispatchMessageW.restype = LRESULT
user32.DispatchMessageW.argtypes = [LPMSG]
user32.EnumDisplayMonitors.restype = BOOL
user32.EnumDisplayMonitors.argtypes = [HDC, LPRECT, MONITORENUMPROC, LPARAM]
user32.EnumDisplaySettingsW.restype = BOOL
user32.EnumDisplaySettingsW.argtypes = [c_wchar_p, DWORD, POINTER(DEVMODE)]
user32.FillRect.restype = c_int
user32.FillRect.argtypes = [HDC, LPRECT, HBRUSH]
user32.GetClientRect.restype = BOOL
user32.GetClientRect.argtypes = [HWND, LPRECT]
user32.GetCursorPos.restype = BOOL
user32.GetCursorPos.argtypes = [LPPOINT]

# workaround for win 64-bit, see issue #664
user32.GetDC.argtypes = [c_void_p]  # [HWND]
user32.GetDC.restype = c_void_p     # HDC

user32.GetDesktopWindow.restype = HWND
user32.GetDesktopWindow.argtypes = list()
user32.GetKeyState.restype = c_short
user32.GetKeyState.argtypes = [c_int]
user32.GetMessageW.restype = BOOL
user32.GetMessageW.argtypes = [LPMSG, HWND, UINT, UINT]
user32.GetMonitorInfoW.restype = BOOL
user32.GetMonitorInfoW.argtypes = [HMONITOR, POINTER(MONITORINFOEX)]
user32.GetQueueStatus.restype = DWORD
user32.GetQueueStatus.argtypes = [UINT]
user32.GetSystemMetrics.restype = c_int
user32.GetSystemMetrics.argtypes = [c_int]
user32.GetSystemMenu.restype = HMENU
user32.GetSystemMenu.argtypes = [HWND, BOOL]
user32.LoadCursorW.restype = HCURSOR
user32.LoadCursorW.argtypes = [HINSTANCE, c_wchar_p]
user32.LoadIconW.restype = HICON
user32.LoadIconW.argtypes = [HINSTANCE, c_wchar_p]
user32.MapVirtualKeyW.restype = UINT
user32.MapVirtualKeyW.argtypes = [UINT, UINT]
user32.MapWindowPoints.restype = c_int
user32.MapWindowPoints.argtypes = [
    HWND, HWND, c_void_p, UINT]  # HWND, HWND, LPPOINT, UINT
user32.MsgWaitForMultipleObjects.restype = DWORD
user32.MsgWaitForMultipleObjects.argtypes = [
    DWORD, POINTER(HANDLE), BOOL, DWORD, DWORD]
user32.PeekMessageW.restype = BOOL
user32.PeekMessageW.argtypes = [LPMSG, HWND, UINT, UINT, UINT]
user32.PostThreadMessageW.restype = BOOL
user32.PostThreadMessageW.argtypes = [DWORD, UINT, WPARAM, LPARAM]
user32.RegisterClassW.restype = ATOM
user32.RegisterClassW.argtypes = [POINTER(WNDCLASS)]
user32.RegisterHotKey.restype = BOOL
user32.RegisterHotKey.argtypes = [HWND, c_int, UINT, UINT]
user32.ReleaseCapture.restype = BOOL
user32.ReleaseCapture.argtypes = list()

# workaround for win 64-bit, see issue #664
user32.ReleaseDC.argtypes = [c_void_p, c_void_p]  # [HWND, HDC]
user32.ReleaseDC.restype = c_int32                # c_int

user32.ScreenToClient.restype = BOOL
user32.ScreenToClient.argtypes = [HWND, LPPOINT]
user32.SetCapture.restype = HWND
user32.SetCapture.argtypes = [HWND]
user32.SetClassLongW.restype = DWORD
user32.SetClassLongW.argtypes = [HWND, c_int, LONG]
if IS64:
    user32.SetClassLongPtrW.restype = ULONG
    user32.SetClassLongPtrW.argtypes = [HWND, c_int, LONG_PTR]
else:
    user32.SetClassLongPtrW = user32.SetClassLongW
user32.SetCursor.restype = HCURSOR
user32.SetCursor.argtypes = [HCURSOR]
user32.SetCursorPos.restype = BOOL
user32.SetCursorPos.argtypes = [c_int, c_int]
user32.SetFocus.restype = HWND
user32.SetFocus.argtypes = [HWND]
user32.SetForegroundWindow.restype = BOOL
user32.SetForegroundWindow.argtypes = [HWND]
user32.SetTimer.restype = UINT_PTR
user32.SetTimer.argtypes = [HWND, UINT_PTR, UINT, TIMERPROC]
user32.SetWindowLongW.restype = LONG
user32.SetWindowLongW.argtypes = [HWND, c_int, LONG]
user32.SetWindowPos.restype = BOOL
user32.SetWindowPos.argtypes = [HWND, HWND, c_int, c_int, c_int, c_int, UINT]
user32.SetWindowTextW.restype = BOOL
user32.SetWindowTextW.argtypes = [HWND, c_wchar_p]
user32.ShowCursor.restype = c_int
user32.ShowCursor.argtypes = [BOOL]
user32.ShowWindow.restype = BOOL
user32.ShowWindow.argtypes = [HWND, c_int]
user32.TrackMouseEvent.restype = BOOL
user32.TrackMouseEvent.argtypes = [POINTER(TRACKMOUSEEVENT)]
user32.TranslateMessage.restype = BOOL
user32.TranslateMessage.argtypes = [LPMSG]
user32.UnregisterClassW.restype = BOOL
user32.UnregisterClassW.argtypes = [c_wchar_p, HINSTANCE]
user32.UnregisterHotKey.restype = BOOL
user32.UnregisterHotKey.argtypes = [HWND, c_int]

# Accept drag/drops
shell32.DragAcceptFiles.argtypes = [HWND, BOOL]
# Find out file name
# shell32.DragQueryFile.restype = UINT
# shell32.DragQueryFile.argtypes = [HDROP, UINT, POINTER(c_wchar), UINT]
# clean up memory
shell32.DragFinish.argtypes = [HDROP]
# Drop x, y
shell32.DragQueryPoint.restypes = BOOL
shell32.DragQueryPoint.argtypes = [HDROP, LPPOINT]
