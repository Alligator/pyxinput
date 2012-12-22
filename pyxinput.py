import ctypes, ctypes.wintypes

xinputDLL = ctypes.windll.xinput9_1_0

class XINPUT_VIBRATE(ctypes.Structure):
    _fields_ = [
        ('left_motor', ctypes.wintypes.WORD),
        ('right_motor', ctypes.wintypes.WORD),
    ]


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('buttons', ctypes.c_ushort),
        ('left_trigger', ctypes.c_ubyte),
        ('right_trigger', ctypes.c_ubyte),
        ('l_thumb_x', ctypes.c_short),
        ('l_thumb_y', ctypes.c_short),
        ('r_thumb_x', ctypes.c_short),
        ('r_thumb_y', ctypes.c_short),
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('packet_number', ctypes.c_ulong),
        ('gamepad', XINPUT_GAMEPAD),
    ]


class XBController(object):
    _bitmasks_ = [
        ('up', 0x00000001),
        ('down', 0x00000002),
        ('left', 0x00000004),
        ('right', 0x00000008),
        ('start', 0x00000010),
        ('back', 0x00000020),
        ('lthumb', 0x00000040),
        ('rthumb', 0x00000080),
        ('lshoulder', 0x0100),
        ('rshoulder', 0x0200),
        ('a', 0x1000),
        ('b', 0x2000),
        ('x', 0x4000),
        ('y', 0x8000)
    ]

    _scalefixes_ = [
        ('l_thumb_x', 32767.0),
        ('l_thumb_y', 32767.0),
        ('r_thumb_x', 32767.0),
        ('r_thumb_y', 32767.0),
        ('left_trigger', 255.0),
        ('right_trigger', 255.0),
    ]

    # if scale is set to true, the thumbstick values go from -1 to 1 and the
    # triggers go from 0 to 1
    def __init__(self, scale=True, number=0):
        self.number = number
        self.scale = scale
        xinputDLL.XInputSetState(ctypes.c_long(self.number), ctypes.c_void_p())

    # Returns the current state of the controller. A dictionary of the following
    # format is returned::
    # 
    #     {
    #         'buttons': {
    #             'a': False, 'b': False, 'back': False, 'down': False,
    #             'left': False, 'lshoulder': False, 'lthumb': False, 'right': False,
    #             'rshoulder': False, 'rthumb': False, 'start': False, 'up': False,
    #             'x': False, 'y': False
    #          },
    #          'l_thumb_x': -0.0717490157780694,
    #          'l_thumb_y': 0.1239661854915006,
    #          'left_trigger': 0.0,
    #          'r_thumb_x': 0.08972441785943175,
    #          'r_thumb_y': 0.03860591448713645,
    #          'right_trigger': 0.0
    #     }
    def getstate(self):
        state = XINPUT_STATE()
        xinputDLL.XInputGetState(ctypes.c_long(self.number), ctypes.byref(state))
        out = {}
        for attr in XINPUT_GAMEPAD._fields_:
            if attr[0] == 'buttons':
                out[attr[0]] = self._buildbuttons_(getattr(state.gamepad, attr[0]))
            else:
                out[attr[0]] = getattr(state.gamepad, attr[0])
        if self.scale:
            for fix in self._scalefixes_:
                out[fix[0]] = out[fix[0]] / fix[1]
            return out
        else:
            return out

    def _buildbuttons_(self, bval):
        buttons = {}
        for mask in self._bitmasks_:
            buttons[mask[0]] = bool(bval & mask[1])
        return buttons

    def vibrate(self, lamount, ramount=None):
        if ramount == None:
            ramount = lamount
        if self.scale:
            # clamp that value
            lamount = sorted((0, lamount, 1))[1]
            ramount = sorted((0, ramount, 1))[1]
            rvamount = int(lamount * 65535)
            lvamount = int(ramount * 65535)
        else:
            lvamount = sorted((0, lamount, 65535))[1]
            rvamount = sorted((0, ramount, 65535))[1]
        vinfo = XINPUT_VIBRATE()
        vinfo.left_motor = ctypes.wintypes.WORD(rvamount)
        vinfo.right_motor = ctypes.wintypes.WORD(lvamount)
        xinputDLL.XInputSetState(ctypes.c_long(self.number), ctypes.byref(vinfo))
