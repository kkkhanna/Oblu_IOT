'''
Script for collecting inertial calibration data in combination with a
calibration body providing a number of orientation for static placement
of the IMU array. Following the collection of data from the sides, the calibration parameters
(scale factor,array alignment,internal alignment,bias) are estimated and
a calibration matrix for the whole array is generated. Finally,
calibration code is generated and graphs are plotted.

#Change the com port before running the script

Authors: Rahul Tiwari, Jaya sandhya M

#
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari, Jaya sandhya M   | Initial Release
#
#
#
'''

import math as m
import serial
from board_settings import b_settings as set_board
from mimu_parse_bin import mimu_parse_bin
from extract_stationary_segments import extract_stationary_segments
from MIMU_calib_param_est import MIMU_calib_param_est
from calibration_matrix import calibration_matrix
from code_generation import code_generation
from MIMU_plot_calib import MIMU_plot_calib
import matplotlib.pyplot as plt
import os.path
import sys
import tkMessageBox
import numpy as np
import time

com_port = '/dev/ttyACM0'          #com port value
g_local = 9.8               #default value for gravity
nr_sides=20                 #no. of sides to be measured
y_meas = np.zeros([1, 1])
global cholQinv
cholQinv = np.zeros([1, 1])

def open_device(device, rate):  # to open serial port . It returns serial port instance
    print "Opening Serial device", device
    btserial = serial.Serial(device, rate)
    return btserial


def read_device(device, length):  # to read coming data packets from com port,length = packet size
    buffer = []
    buffer = device.read(length)
    return buffer


def write_device(device, buffer):  # to send command packets to the deivce
    device.write(buffer)
    device.flushOutput()


def gravity(l, h):          #find g_local value using lattitude and altitude
    l *= m.pi / 180
    gamma = 9.780327 * (1 + 0.0053024 * (m.sin(l)) ** 2 - 0.0000058 * (m.sin(2 * l)) ** 2)
    return gamma - ((3.0877e-6) - (0.004e-6) * (m.sin(l)) ** 2) * h + (0.072e-12) * h ** 2

def cell(rows):     #create a emply matrix with null values of size no. of rows
    lst = []
    for i in range(0,rows):
        lst.append([])

    return lst


# Parameters
internalMisalignment = True  # Model internal misalignment or not- always true
covarianceWeighting = False #always false
covarianceWeightingFile = './Calibration_OBLU/static_20150224_225453_1'
target_board = 'OBLU'  # OBLU
g_local = gravity(26, 0)  # Kanpur (latitude, altitude)
print "g_local",g_local

# System settings
scale_acc = 1.0 / 2048.0 * 9.80665
scale_gyro = 1.0 / 16.4
calib_gain = 2 ** 15
com = 1

# Open serial port
try:
    baudrate=115200   #460800
    com = open_device(com_port, baudrate)
except serial.SerialException as e:
    tkMessageBox.showerror("oops", "%s\nPlease restart the device and com port and try again"%e.message)
    sys.exit(1)


# Board settings
[nr_imus, C_nom, command] = set_board(target_board,com)

# Calculate desired time on each side for pacing sound
desired_nr_samples = 600                # Approx. number of samples per side
freq = 1000*pow(2, (1-(command[5] % 64)))   # Sampling frequency
time_side = desired_nr_samples/freq    # Time on each side

print " "
print "Script for logging calibration data sets with wireless MIMU platform and icosahedron rig."
print "Please verify that the platform is warmed up."
print " "
raw_input('Place body with side 1 up and press any key')

#initialising variables
calibration_measurements = []   #ndarray where the data valus are to be stored
side_counter=1 #current side
tot_counter=0  #total sides measured
v_side=0       #no. of valid sides
inv_side=0     #no. of invalid sides

#Loop over the body sides
while True:
    time.sleep(1)   #This is to let potential vibrations from the key press die out
    print('\nStarting process...')

    # Make sure data is read from the IMUs
    write_device(com, [48, 19, 0, 0, 67])
    # print read_device(com, 4).encode('hex') # GTS

    # Tellopenshoe to output inertial data
    write_device(com, command)
    # print read_device(com, 4).encode # GTS

    # Open binary file for saving inertial data
    filename = 'imu_data.bin'
    log_data = open(filename, 'wb')

    #Logg data_length amount of data
    t_end = time.clock() + time_side;
    while t_end - time.clock() > 0:
        if com.inWaiting() > 0:
            pkt = com.read()
            log_data.write(pkt)

    #stop output and close file
    write_device(com, [34, 0, 34])
    log_data.close()

    #Parse the data
    inertial_data, time_stamps, raw_data = mimu_parse_bin(filename, nr_imus)
    inertial_data = np.transpose(inertial_data)

    #Add data to estimation data structure
    cal_meas, valid_counter = extract_stationary_segments(inertial_data, C_nom,side_counter)

    #save the status/data of the recorded side
    side_rem = nr_sides - side_counter
    if valid_counter == 1: #save the data if valid to the data array
        calibration_measurements.append(cal_meas[0])
        v_side = v_side + 1

    else:
        inv_side = inv_side + 1

    #print status after each side
    print"Faces remaining         = %d:" % side_rem
    print"Valid faces recorded    = %d:" % v_side
    print"Invalid faces recorded  = %d:" % inv_side

    #done with the side
    side_counter = side_counter + 1
    if side_counter <= nr_sides: #get user input
        select=raw_input('\nReject[r]/abort[a]/accept[any other key] (and place body with side %d up)'%side_counter)

        if select=='r': #discard the data collected
            side_counter = side_counter - 1
            if valid_counter == 1:
                v_side = v_side - 1
                calibration_measurements.pop()
            else:
                inv_side = inv_side - 1
        elif select=='a':
            print('Calibration was aborted.')
            break;

    else:
        select = raw_input('\nReject[r]/abort[a]/finish[any other key]') #get user input

        if select == 'a':
            print('Calibration was aborted.')
            break;
        elif select == 'r': #discard the data of the last side
            side_counter = side_counter - 1;
            if valid_counter == 1:
                v_side = v_side - 1
                calibration_measurements.pop()
            else:
                inv_side = inv_side - 1
        else:
            # Post processing of all the data collected
            # Check that we have sufficient number of sides
            print "Number of detected (sufficiently stationary) sides: %d\n\n" % v_side
            if v_side < 12:
                print "To few sides recorded. Aborting."
                sys.exit(1)

            # Estimate and save the calibration parameters
            print "\nEstimating calibration parameters (this may take a while)"
            theta, y_cal_mean = MIMU_calib_param_est(calibration_measurements, nr_imus, C_nom, scale_acc, scale_gyro,v_side,internalMisalignment, covarianceWeighting, covarianceWeightingFile,g_local)
            print "Calibration result: "
            print theta

            # Calculate and generate code for calibration matrix
            print "\nGenerating calibration code files"
            acc, gyro, C_int, b_acc_int, b_gyro_int = calibration_matrix(theta, 1 / scale_acc, 1 / scale_gyro, C_nom,
                                                                         calib_gain)

            if covarianceWeighting:
                # TODO in next version
                # load(covarianceWeightingFile,'inertial_data2');
                # W = covariance_weighting(inertial_data2,double(C_int),nr_imus);
                # clear('inertial_data2');
                # [C_int,b_acc_int,b_gyro_int] = calibration_matrix_with_cov_weighting(theta,1/scale_acc,1/scale_gyro,C_nom,calib_gain,W);
                print "TDOD Covariance weighting"

            #generate .h file
            calib_filename = 'user_calibration_' + target_board + '.h'
            code_generation(acc, gyro, C_int, b_acc_int, b_gyro_int, nr_imus, calib_filename)
            print 'Calibration matrix:'
            print b_acc_int
            print b_gyro_int
            print C_int
            print "\n\nUser calibration file generated: %s" % calib_filename

            # Plot calibration data (with and without compensation for calibration)
            print '\nPlotting calibration data'
            MIMU_plot_calib(calibration_measurements, nr_imus, C_int, C_nom, theta, scale_acc, calib_gain, b_acc_int,
                            scale_gyro, b_gyro_int, v_side)
            plt.show()
            break;

#remove all temp files
if os.path.isfile("stop"):
    os.remove("stop")
if os.path.isfile("imu_data.bin"):
    os.remove("imu_data.bin")

#close com port
com.close()

