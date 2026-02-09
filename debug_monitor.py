# Debug Monitor Script

import datetime
import logging

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, filename='debug_monitor.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Debugging function

def debug_monitor():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.debug(f'Current Date and Time (UTC): {current_time}')

if __name__ == '__main__':
    debug_monitor()
