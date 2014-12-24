_kernel32 = DebugLibrary(windll.kernel32)
_user32 = DebugLibrary(windll.user32)
_shell32 = DebugLibrary(windll.shell32)
_user32.UnregisterHotKey.restype = BOOL
_user32.UnregisterHotKey.argtypes = [HWND, c_int]

# Accept drag/drops
_shell32.DragAcceptFiles.argtypes = [HWND, BOOL]
# Find out file name
#_shell32.DragQueryFile.restype = UINT
#_shell32.DragQueryFile.argtypes = [HDROP, UINT, POINTER(c_wchar), UINT]
# clean up memory
_shell32.DragFinish.argtypes = [HDROP]
# Drop x, y
_shell32.DragQueryPoint.restypes = BOOL
_shell32.DragQueryPoint.argtypes = [HDROP, LPPOINT]
