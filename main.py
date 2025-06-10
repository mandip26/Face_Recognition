import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication

from gui.main_window import AttendanceSystemGUI
from data.ensure_paths import ensure_data_paths


async def main():
    def close_future(future, loop):
        loop.call_later(0.1, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Ensure data paths exist and files are in the right places
    ensure_data_paths()

    window = AttendanceSystemGUI()
    window.show()

    app.lastWindowClosed.connect(lambda: close_future(future, loop))

    try:
        await future
    except asyncio.CancelledError:
        # This is expected when closing the application
        pass
    finally:
        # Clean shutdown
        if hasattr(window, 'is_running') and window.is_running:
            await window.stop_recognition_async()


if __name__ == "__main__":
    try:
        qasync.run(main())
    except asyncio.CancelledError:
        # Handle the cancellation gracefully
        print("Application closed normally")
    except Exception as e:
        print(f"Application error: {str(e)}")