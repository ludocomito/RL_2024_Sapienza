import glob
import queue
import sys
from typing import List, Optional

import serial


# From https://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
class CustomQueue(queue.Queue):
    """
    A custom queue subclass that provides a :meth:`clear` method.
    """

    def clear(self) -> None:
        """
        Clears all items from the queue.
        """

        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError("task_done() called too many times")
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
            self.queue.clear()
            self.not_full.notify_all()


# From https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def get_serial_ports() -> List[str]:
    """
    Lists serial ports.


    :return: A list of available serial ports
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise OSError("Unsupported platform")

    results = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            results.append(port)
        except (OSError, serial.SerialException):
            pass
    return results


def open_serial_port(
    serial_port: Optional[str] = None,
    baudrate: int = 115200,
    timeout: Optional[int] = 0,
    write_timeout: int = 0,
) -> serial.Serial:
    """
    Try to open serial port with Arduino
    If not port is specified, it will be automatically detected

    :param serial_port:
    :param baudrate:
    :param timeout: None -> blocking mode
    :param write_timeout:
    :return: (Serial Object)
    """
    # Open serial port (for communication with Arduino)
    if serial_port is None:
        serial_port = get_serial_ports()[0]
    # timeout=0 non-blocking mode, return immediately in any case, returning zero or more,
    # up to the requested number of bytes
    return serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout, writeTimeout=write_timeout)
