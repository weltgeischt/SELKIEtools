import logging

def str_to_sec(time_str):
    if time_str.count('.'):
        reststr,subsec0 = time_str.split('.')
        subsec = int(subsec0)
    else:
        subsec = 0
        reststr = time_str

    n_u = reststr.count(':')
    if n_u == 0:
        ss = int(reststr)
        hh, mm = 0, 0
    elif n_u == 1:
        mm,ss = reststr.split(':')
        hh = 0
    elif n_u == 2:
        hh,mm,ss = reststr.split(':')

    return int(hh) * 60*60 + int(mm) * 60 + int(ss) + 0.1*subsec


def seconds_to_min_sec(x,pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes}:{seconds:02d}"





class Logger(logging.getLoggerClass()):
    def __init__(self, name, log_dir=None,level=logging.INFO):
        # Create custom logger logging all five levels
        super().__init__(name)
        self.setLevel(level)

        # Create stream handler for logging to stdout (log all five levels)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.stdout_handler.setLevel(level)
        self.stdout_handler.setFormatter(logging.Formatter('%(message)s'))
        #self.enable_console_output()
        self.addHandler(logging.StreamHandler(sys.stdout))
        # Add file handler only if the log directory was specified
        self.file_handler = None
        if log_dir:
            self.add_file_handler(name, log_dir)

    def add_file_handler(self, name, log_dir):
        """Add a file handler for this logger with the specified `name` (and
        store the log file under `log_dir`)."""
        # Format for file log
        fmt = '%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s'
        formatter = logging.Formatter(fmt)

        # Determine log path/file name; create log_dir if necessary
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_name = f'{str(name).replace(" ", "_")}_{now}'
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print('{}: Cannot create directory {}. '.format(
                    self.__class__.__name__, log_dir),
                    end='', file=sys.stderr)
                log_dir = '/tmp' if sys.platform.startswith('linux') else '.'
                print(f'Defaulting to {log_dir}.', file=sys.stderr)

        log_file = os.path.join(log_dir, log_name) + '.log'

        # Create file handler for logging to a file (log all five levels)
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)
        self.addHandler(self.file_handler)
