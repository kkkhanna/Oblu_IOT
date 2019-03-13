# Function generates the calibration matrix and other important values to be used for calibration
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari                   | Initial Release
#

import numpy as np
import numpy.linalg as lin
import math

# convert a matrix to a list
def convert_lin(mat):
    linear_list = []
    for i in range(0,len(mat[0])):
        a = mat[:,i]

        for value in a:
            linear_list.append(value)

    return linear_list


def calibration_matrix(theta,theta_acc_scale,theta_gyro_scale,C_nom,calib_gain):
    print "In calibration matrix.py"

    nr_imus = len(theta)
    k = theta[:, 0:3]                           # No units
    b_acc = theta[:, 3:6]*theta_acc_scale       # In bits
    s = theta[:, 6:9]                           # In radians
    e = theta[:, 9:12]                          # In radians
    b_gyro = theta[:, 12:15]*theta_gyro_scale  # In bits

    C = np.zeros((32, 24),float)
    ba_acc = np.zeros((32, 3), float)
    bg_gyro = np.zeros((32, 3),float)
    # Loop over IMUs
    for m in range (0,nr_imus):
        R = np.reshape(C_nom[m, 0:9], (3, 3))
        K = np.diag(k[m,:])
        S = np.eye(3)
        S[0, 1] = -s[m, 0]
        S[0, 2] = s[m, 1]
        S[1, 2] = -s[m, 2]
        E = np.eye(3)
        E[0, 1] = e[m, 2]
        E[0, 2] = -e[m, 1]
        E[1, 2] = e[m, 0]
        E[1, 0] = - e[m, 2]
        E[2, 0] = e[m, 1]
        E[2, 1] = -e[m, 0]
        tmp = lin.inv(np.dot(np.dot(K, S), E))
        tmp2 = np.dot(tmp, R)
        tmp3 = lin.inv(E)
        tmp4 = np.dot(tmp3, R)
        C[m, 0:9] = convert_lin(tmp2)
        C[m, 9:18]= convert_lin(tmp4)
        C[m, 18:21] = b_acc[m, :]
        C[m, 21:24] = b_gyro[m, :]
        b_acc[m, :] = np.dot(tmp , np.reshape(b_acc[m, :],(len(b_acc[m]),1))).transpose()
        b_gyro[m, :] = np.dot(tmp3, b_gyro[m, :].transpose()).transpose()
        ba_acc[m, :] = b_acc[m, :]
        bg_gyro[m, :] = b_gyro[m, :]

    C /= nr_imus
    C_int = np.round(C * calib_gain * 2 ** math.floor(math.log(nr_imus, 2)))
    C_int = C_int.astype(int)
    b_acc_int = (np.round(sum(b_acc * calib_gain/nr_imus)).transpose()).astype(np.int32)
    b_gyro_int = (np.round(sum(b_gyro * calib_gain / nr_imus)).transpose()).astype(np.int32)
    acc = (np.round(ba_acc * calib_gain / nr_imus)).astype(np.int32)
    gyro = (np.round(bg_gyro * calib_gain / nr_imus)).astype(np.int32)

    return acc, gyro, C_int, b_acc_int, b_gyro_int




