import time
import os


class ProgressBar:
    @staticmethod
    def terminal_size():
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(rows), int(columns)

    def __init__(self, progress_length, prefix="", suffix="", decimals=1,
                 length=50, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            progress_length       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """

        self.progress = 0
        self.progress_length = progress_length
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.printEnd = printEnd

    def increment(self):
        self.progress += 1

        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.progress / self.progress_length))
        filledLength = int(self.length * self.progress // self.progress_length)
        bar = self.fill * filledLength + '-' * (self.length - filledLength)
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.printEnd)

        # Print New Line on Complete
        if self.progress == self.progress_length:
            print()

    def set_progress(self, progress):
        self.progress = progress

        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.progress / self.progress_length))
        filledLength = int(self.length * self.progress // self.progress_length)
        bar = self.fill * filledLength + '-' * (self.length - filledLength)
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.printEnd)

        # Print New Line on Complete
        # if self.progress == self.progress_length:
        #     print()


if __name__ == "__main__":
    bar = ProgressBar(100, length=100)

    for i in range(100):
        time.sleep(0.1)
        bar.increment()
