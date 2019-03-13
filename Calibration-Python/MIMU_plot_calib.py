# Plotting graphs
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari, Jaya sandhya M   | Initial Release


import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import numpy.matlib
import math


def MIMU_plot_calib(calib_meas,nr_imus,C_int,C_nom,theta,acc_scale,calib_gain,b_acc_int,gyro_scale,b_gyro_int,nr_sides):
    print "In file MIMU_plot_calib.py"
    #Prepare the figures
    plt.figure(2)
    plt.grid()
    plt.title('Accelerometer readings')
    plt.xlabel('sample number')
    plt.ylabel('a [m/s^2]')
    plt.figure(3)
    plt.grid()
    plt.title('Gyroscope readings')
    plt.xlabel('sample number')
    plt.ylabel('\omega [deg/s]')


    gyro_tot = []
    acc_tot = []

    # Loop over calibration data sets
    start_plot = 0
    for data_set in range(0,nr_sides):
        (nr_row,nr_data) = calib_meas[data_set].shape
        inert_data = np.double(calib_meas[data_set])
        plt.figure(2)
        for i in range(0,nr_imus):
            R = np.reshape(C_nom[i, 0:9], (3, 3)).transpose()
            data = np.dot(R, inert_data[i * 6 + np.array([0,1,2]), :])
            plt.plot(range(start_plot, start_plot + nr_data), data[0, :]*acc_scale, 'b-')
            plt.plot(range(start_plot, start_plot + nr_data), data[1, :]*acc_scale, 'g-')
            plt.plot(range(start_plot, start_plot + nr_data), data[2, :]*acc_scale, 'r-')
            plt.plot(range(start_plot, start_plot + nr_data), np.sqrt(np.sum(np.power(data[0:3, :]*acc_scale, 2), 0)), color='DarkCyan')

            R = np.reshape(np.double(C_int[i, 0:9]), (3, 3)).transpose()
            data = np.dot(np.dot(R, inert_data[i * 6 + np.array([0,1,2]), :]),acc_scale/calib_gain)  - np.tile(theta[i, 3:6], (nr_data,1)).transpose()
            plt.plot(range(start_plot, start_plot + nr_data), data[0, :], 'c-')
            plt.plot(range(start_plot, start_plot + nr_data), data[1, :], 'm-')
            plt.plot(range(start_plot, start_plot + nr_data), data[2, :], 'y-')
            plt.plot(range(start_plot, start_plot + nr_data), np.sqrt(np.sum(np.power(data[0:3, :], 2), 0)), color='Gold')
        plt.figure(3)
        for i in range(0, nr_imus):
            R = np.reshape(C_nom[i, 0:9], (3, 3)).transpose()
            data = np.dot(R, inert_data[i * 6 + np.array([3,4,5]), :])
            plt.plot(range(start_plot, start_plot + nr_data), data[0, :].transpose() * gyro_scale, 'b-')
            plt.plot(range(start_plot, start_plot + nr_data), data[1, :].transpose() * gyro_scale, 'g-')
            plt.plot(range(start_plot, start_plot + nr_data), data[2, :].transpose() * gyro_scale, 'r-')
            R = np.reshape(np.double(C_int[i, 9:18]), (3, 3)).transpose()
            data = np.dot(np.dot(R, inert_data[i * 6 + np.array([3,4,5]), :]), gyro_scale / calib_gain) - np.tile(theta[i, 9:12], (nr_data, 1)).transpose()
            plt.plot(range(start_plot, start_plot + nr_data), data[0, :], 'c-')
            plt.plot(range(start_plot, start_plot + nr_data), data[1, :], 'm-')
            plt.plot(range(start_plot, start_plot + nr_data), data[2, :], 'y-')
            #plt.show()
        inertial_data_comp = np.int32(np.zeros((6,nr_data),int))
        for i in range(0, nr_data):
            for m in range(0, nr_imus):
                u_tmp = np.int32(np.zeros((6, 1), int))
                for j in range(0, 3):
                    # Integer
                    u_tmp[j] += C_int[m, (j * 3) + 0] * np.int32(calib_meas[data_set][6 * m + 0, i])
                    u_tmp[j] += C_int[m, (j * 3) + 1] * np.int32(calib_meas[data_set][6 * m + 1, i])
                    u_tmp[j] += C_int[m, (j * 3) + 2] * np.int32(calib_meas[data_set][6 * m + 2, i])

                    u_tmp[j + 3] += C_int[m, j * 3 + 9] * np.int32(calib_meas[data_set][6 * m + 3, i])
                    u_tmp[j + 3] += C_int[m, j * 3 + 10] * np.int32(calib_meas[data_set][6 * m + 4, i])
                    u_tmp[j + 3] += C_int[m, j * 3 + 11] * np.int32(calib_meas[data_set][6 * m + 5, i])

                # This division (shift) will cause an insignificant bias
                tmp=np.floor(u_tmp/(2**(np.floor(math.log(nr_imus, 2)))))
                u_tmp = tmp.astype(int).transpose()[0].transpose()
                inertial_data_comp[:, i] += u_tmp

            inertial_data_comp[0:3, i] -= b_acc_int
            inertial_data_comp[3:6, i] -= b_gyro_int
        plt.figure(2)
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[0, :]) / calib_gain * acc_scale, 'k-')
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[1, :]) / calib_gain * acc_scale, 'k-')
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[2, :]) / calib_gain * acc_scale, 'k-')
        plt.plot(range(start_plot, start_plot + nr_data), np.sqrt(np.double(inertial_data_comp[0,:])**2 + np.double(inertial_data_comp[1,: ])**2 + np.double(inertial_data_comp[2,:])**2)/calib_gain * acc_scale, 'k--',linewidth=2)
        acc_tot = [acc_tot, np.sqrt(np.sum((np.double(inertial_data_comp[0:3, :]) / calib_gain * acc_scale)**2))]
        plt.figure(3)
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[3, :]) / calib_gain * gyro_scale, 'k-')
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[4, :]) / calib_gain * gyro_scale, 'k-')
        plt.plot(range(start_plot, start_plot + nr_data), np.double(inertial_data_comp[5, :]) / calib_gain * gyro_scale, 'k-')
        gyro_tot = [gyro_tot, np.double(inertial_data_comp[3:6, :]) / calib_gain * gyro_scale]
        #plt.show()
        start_plot += nr_data

    plt.show(block=False)





