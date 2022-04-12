import os, time
import datetime

class FileWrite:
    def __init__(self):
        pass

    def writeWords(self, symbol, msg):
        # Current date for make directory
        output_save_folder_path = './log/'
        output_path = os.path.join(output_save_folder_path, time.strftime('%Y%m', time.localtime(time.time())))
        today = datetime.date.today().strftime('%y%m%d')

        if not os.path.exists(output_save_folder_path):
            os.mkdir(output_save_folder_path)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        filename = f"./{output_path}/OBOS_{symbol}-{today}.txt"

        # If there is no file then make blank new file
        if not os.path.isfile(filename):
            with open(filename, 'w') as file:
                pass

        with open(filename, 'a+', encoding='UTF8') as file:
            file.write(msg)



