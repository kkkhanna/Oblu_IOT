# Function to parse the data from the sensor and checks if the pkt is valid or not. Discards if invalid
#
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari, Jaya sandhya M   | Initial Release
#
#

import struct
import os
import sys
import numpy as np
import re
import tkMessageBox
MAX_FILENAME_SIZE = 1024

# get checksum
def get_checksum(pkt, start):  # to get checksum from the packet
    return struct.unpack("!H", pkt[start:start+2])[0]

# calculate checksum
def cal_checksum(pkt, end):  # to calculate checksum of a packet
    checksum = 0
    a = pkt[0:end].encode('hex')
    x=0
    y=2
    for i in range(0,len(a)/2):
        checksum += int(a[x:y], 16)
        x +=2
        y +=2
    return checksum

# parse the data from the sensor
def mimu_parse_bin(filename, nr_imus):
    #print "In file mimu_parse_bin.py"
    nof_imus = nr_imus
    PAYLOAD_SIZE = 4 + 12 * nof_imus
    PACKET_SIZE = 4 + PAYLOAD_SIZE + 2
    nof_data_values = 6 * nof_imus
    data_values_size = 2 * nof_data_values
    filesize = os.stat(filename).st_size
    max_elts = filesize / PACKET_SIZE
    inertial_data = []
    time_data = []
    raw_data = []
    count = 0
    error_count = 0
    data = file(filename, "rb")
    pkt = data.read(PACKET_SIZE)
    counte = 0
    while len(pkt)==PACKET_SIZE:

        s1= pkt.encode("hex")
        (start_code, pkt_num, payload_length) = struct.unpack("!BHB", pkt[0:4])
        # Save the pkt if valid
        if start_code == 0xAA and get_checksum(pkt, 4+PAYLOAD_SIZE) == cal_checksum(pkt, PACKET_SIZE-2):
            inertial_data.append(struct.unpack("!hhhhhhhhhhhhhhhhhhhhhhhh", pkt[8:data_values_size+8]))
            time_data.append(struct.unpack("!L", pkt[4:8]))
            raw_data.append(struct.unpack("!Lhhhhhhhhhhhhhhhhhhhhhhhh", pkt[4:data_values_size+8]))
            pkt = data.read(PACKET_SIZE)
            counte = 0
            count += 1
        #   search for a new header AA and get a new packet
        elif re.search(b'[\d|\w]+aa.*', s1):
                lst = re.findall(b'[\d|\w]+(aa.*)', s1)
                strrem = lst[0]  # t=np.asarray(lst)
                lenght = len(strrem)/2
                pktrem=pkt[-lenght:]
                newlen = PACKET_SIZE - lenght
                pkt = data.read(newlen)
                pkt=pktrem+pkt
        # get a new packet if not valid
        else:
            pkt = data.read(PACKET_SIZE)
            # exit the code if the packet is detecting wrong continuously for more than 5 times
            counte += 1
            if counte > 5:
                counte = 0
                tkMessageBox.showinfo("Oops",
                                      "Something went wrong please restart the device and run the process again !")
                stop = file("error", 'w')
                stop.close()
                sys.exit(1)
    #print "total packets : ",count
    #print "Leaving file mimu_parse_bin.py"
    inertial_data = np.reshape(inertial_data,(len(inertial_data),len(inertial_data[0])))
    return inertial_data, time_data, raw_data