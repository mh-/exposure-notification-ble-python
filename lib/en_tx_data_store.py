import base64


class ENTxDataStore:
    def __init__(self, tx_raw_data_file_name):
        self.tek_data_file = open(tx_raw_data_file_name, 'a')
        self.tek_data_file.write("TEK_Roll_Interval_i;TEK;TEK-base64\n")

    def __del__(self):
        self.tek_data_file.close()

    def write(self, i, tek):
        self.tek_data_file.write("%d;%s;%s\n" % (i, tek.hex(), base64.b64encode(tek).decode(encoding="UTF-8")))
        self.tek_data_file.flush()
