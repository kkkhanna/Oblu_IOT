# Function checks whether the side data recorded is valid or invalid.
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari, Jaya sandhya M   | Initial Release


import numpy as np
import matplotlib.pyplot as plt #import module to plot
from termcolor import colored   #import module to print in colors


def numel(array):
    count = 0
    for i in array:
        if i ==True:
            count +=1

    return count


def find(a, b):
    lst = []
    for i in range(0,len(a)):
        if a[i] & b[i] == 1:
            lst.append(i)
    return lst


def cell(rows):
    lst = []
    for i in range(0,rows):
        lst.append([])

    return lst


def get_last_chosen(selected):
    a = selected
    val = 0
    i = len(a)
    while i!=0:
        i -= 1
        if a[i] != 0:
            val = i
            break
    return int(val)


def extract_stationary_segments(inertial_data, C_nom, face_counter):
    half_window_size = 25
    min_period = 100
    max_period = 3000
    threshold_factor = 3
    min_diff_of_sets = 500
    nr_imus = len(C_nom)
    nr_data = len(inertial_data[0])
    # converting inertial data into float
    inertial_data_double = inertial_data
    #print inertial_data_double.shape
    comb_inert = np.zeros((6, nr_data), np.double)
    for i in range(0, nr_imus):
        r1 = np.hstack((np.reshape(C_nom[i, 0:9], (3, 3)), np.zeros((3, 3), np.double)))
        r2 = np.hstack((np.zeros((3, 3), np.double), np.reshape(C_nom[0 + i, 9:18], (3, 3))))
        R = np.vstack((r1, r2))
        comb_inert += np.dot(R, inertial_data_double[6 * i:(6 * i) + 6, :])

    window_size = 2 * half_window_size + 1
    running_mean = np.zeros((len(comb_inert), len(comb_inert[0])), np.double)
    running_var = np.zeros((len(comb_inert), len(comb_inert[0])), np.double)
    comb_inert = np.hstack((np.zeros((6, half_window_size), np.double), comb_inert, np.zeros((6, half_window_size), np.double)))

    # Calculate running mean
    running_mean[:, 0] = np.sum(comb_inert[:, 0:window_size], 1)
    for i in range(1, nr_data):
        running_mean[:, i] = running_mean[:, i - 1] + (comb_inert[:, i - 1 + window_size] - comb_inert[:, i - 1])

    running_mean /= window_size

    # Calculate variance
    for i in range(0, nr_data):
        t = running_mean[:, i]
        tmp = np.reshape(t, (len(running_mean), 1))
        tile = np.tile(tmp, (1, window_size))
        running_var[:, i] = np.sum((comb_inert[:, i:i + window_size]-tile)**2, 1)


    min_var = np.min(running_var, 1)
    min_var = np.reshape(min_var, (1,len(min_var)))
    stat = np.dot((min_var**-1), running_var)

    threshold = threshold_factor * np.min(stat)
    threshold = float(threshold)
    larger = []
    smaller = []
    for i in stat[0]:
        if i>threshold:
            larger.append(1)
        else:
            larger.append(0)
    for i in stat[0]:
        if i <= threshold:
            smaller.append(1)
        else:
            smaller.append(0)
    stop = find(larger[1:len(larger)], smaller[0:len(smaller) - 1])
    start = find(smaller[1:len(smaller)], larger[0:len(larger) - 1])
    nr_sides = min(len(start),len(stop))

    selected = np.zeros((nr_sides, 1), np.double)
    calibration_measurements = cell(nr_sides + 1)
    start_and_end_points = np.zeros((nr_sides+1, 2), np.double)
    side_counter = 0
    if nr_sides>0: # min 1 value is needed to proceed
        if stop[0] - start[0] > min_period:
            side_counter += 1
            selected[0] = 1
            if stop[0] - start[0] < max_period:
                calibration_measurements[side_counter] = inertial_data[:, start[0]:stop[0]+1]
                start_and_end_points[side_counter, :] = [start[0], stop[0]]
            else:
                calibration_measurements[side_counter] = inertial_data[:, start[0]:start[0]+1+ max_period]
                start_and_end_points[side_counter, :] = [start[0], start[0] + max_period]
        for i in range(1, nr_sides):

            if stop[i] - start[i] > min_period:
                last_chosen = get_last_chosen(selected)  ################################################
                if last_chosen != 0:
                    if sum(abs(running_mean[0: 3, stop[last_chosen]]-running_mean[0:3, start[i]])) > min_diff_of_sets:
                        side_counter += 1
                        selected[i] = 1
                    else:
                        if stop[i]-start[i] < stop[last_chosen]-start[last_chosen]:
                            continue
                else:
                    side_counter += 1
                    selected[i] = 1
                if stop[i] - start[i] < max_period:
                    calibration_measurements[side_counter] = inertial_data[:, start[i]:stop[i]+1]
                    start_and_end_points[side_counter, :] = [start[i], stop[i]]
                else:
                    calibration_measurements[side_counter] = inertial_data[:, start[i]:start[i]+1+ max_period]
                    start_and_end_points[side_counter, :] = [start[i], start[i] + max_period]

        #print "after loop calibration m",calibration_measurements
        if side_counter-1!=nr_sides:
            calibration_measurements = calibration_measurements[1:side_counter+1]
            start_and_end_points = start_and_end_points[1:side_counter+1,:]

    scale_acc = (1.0 / 2048) * 9.80665
    scale_gyro = 1 / 16.4
    
    comb_inert = comb_inert[:, half_window_size:- half_window_size]

    plt.subplot(211)
    plt.title('Selected periods -- accelerometer readings')
    #plt.xlabel('sample number')
    plt.ylabel('a [m/s^2]')

    plt.plot(comb_inert[0:3,:].transpose()*scale_acc/nr_imus)
    plt.grid(True)
    axes = plt.gca()
    ylim = axes.get_ylim()
    xlim = axes.get_xlim()

    plt.subplot(212)
    plt.title('Selected periods -- gyroscope readings')
    plt.xlabel('sample number')
    plt.ylabel('\omega [deg/s]')
    plt.plot(comb_inert[3:6,:].transpose()*scale_gyro/nr_imus)
    #plt.show()

    if len(start_and_end_points)==0:
        print colored('Warning: INVALID results for face #%d. Repeat recommended.', 'red') % face_counter
        print colored('Note: Minimum faces required with VALID results = 12.','red')
        print colored('Less than 12 faces with valid results may spoil the outcome', 'red')
        valid_counter=0
    else:
        print colored('Success: VALID results for face #%d.','green') % face_counter
        valid_counter=1

    '''
    fig2 = plt.figure(2)
    plt.subplot(211)
    plt.plot(running_var[1:3,:].transpose())
    plt.grid(True)
    plt.subplot(212)
    plt.plot(running_var[4:6,:].transpose())
    plt.grid(True)
    plt.show(block=False)
    #plt.close()


    fig3 = plt.figure(3)
    plt.plot(stat[0])
    plt.grid(True)
    plt.show(block=False)
    #plt.close()
    '''
    return calibration_measurements, valid_counter


