import curses
from queue import Queue
from threading import Event, Lock
from time import sleep


INPUT_EXIT = 1
INPUT_TOGGLE_INFO = 2

RGB_256 = (
    ((0, 0, 0), 1),
    ((229, 34, 0), 2),
    ((0, 194, 0), 3),
    ((199, 196, 0), 4),
    ((3, 67, 200), 5),
    ((201, 49, 199), 6),
    ((0, 197, 199), 7),
    ((199, 199, 199), 8),
    ((104, 104, 104), 9),
    ((255, 110, 103), 10),
    ((96, 250, 104), 11),
    ((255, 252, 102), 12),
    ((105, 113, 255), 13),
    ((255, 119, 255), 14),
    ((98, 253, 255), 15),
    ((255, 255, 255), 16),
    ((0, 0, 0), 17),
    ((2, 17, 115), 18),
    ((4, 26, 153), 19),
    ((6, 35, 189), 20),
    ((8, 43, 223), 21),
    ((11, 51, 255), 22),
    ((0, 111, 0), 23),
    ((0, 113, 114), 24),
    ((0, 115, 153), 25),
    ((0, 117, 189), 26),
    ((0, 119, 223), 27),
    ((0, 121, 255), 28),
    ((0, 149, 0), 29),
    ((0, 150, 114), 30),
    ((0, 151, 153), 31),
    ((0, 153, 189), 32),
    ((0, 154, 223), 33),
    ((0, 156, 255), 34),
    ((0, 184, 0), 35),
    ((0, 185, 114), 36),
    ((0, 186, 153), 37),
    ((0, 187, 189), 38),
    ((0, 188, 223), 39),
    ((0, 190, 255), 40),
    ((0, 217, 0), 41),
    ((0, 218, 114), 42),
    ((0, 219, 153), 43),
    ((0, 220, 189), 44),
    ((0, 221, 223), 45),
    ((0, 222, 255), 46),
    ((0, 249, 0), 47),
    ((0, 249, 114), 48),
    ((0, 250, 153), 49),
    ((0, 251, 189), 50),
    ((0, 252, 223), 51),
    ((0, 253, 255), 52),
    ((115, 12, 0), 53),
    ((116, 24, 114), 54),
    ((116, 31, 153), 55),
    ((116, 39, 189), 56),
    ((116, 46, 223), 57),
    ((116, 53, 255), 58),
    ((114, 112, 0), 59),
    ((114, 114, 114), 60),
    ((114, 116, 153), 61),
    ((115, 118, 189), 62),
    ((115, 120, 223), 63),
    ((115, 122, 255), 64),
    ((113, 150, 0), 65),
    ((113, 151, 114), 66),
    ((113, 152, 153), 67),
    ((114, 154, 189), 68),
    ((114, 155, 223), 69),
    ((114, 157, 255), 70),
    ((112, 185, 0), 71),
    ((112, 186, 114), 72),
    ((112, 187, 153), 73),
    ((112, 188, 189), 74),
    ((112, 189, 223), 75),
    ((113, 190, 255), 76),
    ((110, 218, 0), 77),
    ((110, 219, 114), 78),
    ((110, 219, 153), 79),
    ((111, 221, 223), 81),
    ((109, 253, 255), 88),
    ((153, 152, 114), 102),
    ((223, 188, 113), 180),
    ((223, 222, 189), 188),
    ((255, 189, 113), 216),
    ((255, 255, 255), 232),
    ((23, 23, 23), 234),
    ((37, 37, 37), 235),
    ((51, 51, 51), 236),
    ((63, 63, 63), 237),
    ((75, 75, 75), 238),
    ((86, 86, 86), 239),
    ((97, 97, 97), 240),
    ((107, 107, 107), 241),
    ((117, 117, 117), 242),
    ((127, 127, 127), 243),
    ((137, 137, 137), 244),
    ((146, 146, 146), 245),
    ((156, 156, 156), 246),
    ((165, 165, 165), 247),
    ((174, 174, 174), 248),
    ((183, 183, 183), 249),
    ((191, 191, 191), 250),
    ((200, 200, 200), 251),
    ((209, 209, 209), 252),
    ((217, 217, 217), 253),
    ((225, 225, 225), 254),
)
RGB_CACHE = {}


def closest_color(r, g, b):
    if (r, g, b) in RGB_CACHE.keys():
        return RGB_CACHE[(r, g, b)]
    best_candidate = 0
    best_distance = 765
    for rgb, candidate in RGB_256:
        distance = abs(r - rgb[0]) + abs(g - rgb[1]) + abs(b - rgb[2])
        if distance < best_distance:
            best_candidate = candidate
            best_distance = distance
    RGB_CACHE[(r, g, b)] = best_candidate
    return best_candidate


def setup(stdscr):
    # curses
    curses.use_default_colors()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    curses.curs_set(False)
    stdscr.timeout(0)

    # prepare input thread mechanisms
    curses_lock = Lock()
    input_queue = Queue()
    quit_event = Event()
    return (curses_lock, input_queue, quit_event)


def graceful_ctrlc(func):
    """
    Makes the decorated function terminate silently on CTRL+C.
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
    return wrapper


def input_thread_body(stdscr, input_queue, quit_event, curses_lock):
    while not quit_event.is_set():
        try:
            with curses_lock:
                key = stdscr.getkey()
        except:
            key = None
        if key in ("q", "Q"):
            input_queue.put(INPUT_EXIT)
        elif key == "i":
            input_queue.put(INPUT_TOGGLE_INFO)
        sleep(0.01)
