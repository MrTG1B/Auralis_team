import dashboard_browser as dbrowser
import server
import time
import threading as th

if __name__ == "__main__":
    serverTh = th.Thread(target=server.run_server, daemon=True)
    serverTh.start()
    dbrowser.run_browser()
    # server.stop_server()
    print("Done")