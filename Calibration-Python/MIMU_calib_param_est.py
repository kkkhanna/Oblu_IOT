#  Script that runs the IMU array calibration described in [1]
#  The script does the following. It loads the raw data and
#  preprocesses it. Thereafter the noise covariances of the data are
#  estimated. Then the initial roll and pitch angles of the platform
#  are estimated. Finally the actual calibration algorithm is
#  processed.
#
#
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari, Jaya sandhya M   | Initial Release
#
#


import numpy as np
import numpy.linalg as lin
import scipy.linalg as lins
import math
from scipy.optimize import least_squares,leastsq
# global variables
global y_meas
global cholQinv
global g_local

#  Cost function used in the calibration of the IMU array. Note that
#  the nonlinear least square optimizer in Matlab requires the cost
#  function to return the individual errors and note the squared sum e of
#  the errors.
#
#  Output:     z       A 3*M*L long vector with all the individual errors
#  Input:      theta   A 9*M-3 long vector with the optimization
def costFunctionArrayInternalMisalignment(theta):
    global y_meas
    global cholQinv
    global g_local

    L = len(y_meas)
    M = len(y_meas[0])
    n = len(y_meas[0][0])
    z = np.zeros((L, M, 3),np.float64)

    for l in range(0, L):

        # Estimate the roll and pitch at the l:th orientation and construct the
        # input vector u^(i)_n.
        roll = theta[2 * l]
        pitch = theta[2 * l + 1]
        u = g_local * np.array([-math.sin(pitch), math.cos(pitch) * math.sin(roll), math.cos(pitch) * math.cos(roll)])

        # Calculate the difference between the estimated and measured output of the M IMUs.
        for m in range(0, M-1):
            K = np.diag(theta[(2 * L) + (12 * m): (2 * L) + (12 * m) + 3])
            S = np.eye(3)
            S[0, 1] = -theta[(2 * L) + (12 * m) + 6]
            S[0, 2] = theta[(2 * L) + (12 * m) + 7]
            S[1, 2] = -theta[(2 * L) + (12 * m) + 8]
            b = theta[(2 * L) + (12 * m) + 3: (2 * L) + (12 * m) + 6]
            E = np.eye(3)

            E[0, 1] = theta[(2 * L) + (12 * m) + 11]
            E[0, 2] = -theta[(2 * L) + (12 * m) + 10]
            E[1, 0] = -theta[(2 * L) + (12 * m) + 11]
            E[1, 2] = theta[(2 * L) + (12 * m) + 9]
            E[2, 0] = theta[(2 * L) + (12 * m) + 10]
            E[2, 1] = -theta[(2 * L) + (12 * m) + 9]
            y_hat = np.dot(np.dot(np.dot(K, S), E), u)  # + b

            z[l, m, :] = np.dot(np.squeeze(cholQinv[l, :, m, :]).transpose(), (y_meas[l, m, :].transpose() - y_hat))

        K = np.diag(theta[2 * L + 12 * (M - 1): 2 * L + 12 * (M - 1) + 3])
        b = theta[2 * L + 12 * (M - 1) + 3:2 * L + 12 * (M - 1) + 6]
        S = np.eye(3)
        S[0, 1] = -theta[2 * L + 12 * (M - 1) + 6]
        S[0, 2] = theta[2 * L + 12 * (M - 1) + 7]
        S[1, 2] = -theta[2 * L + 12 * (M - 1) + 8]
        y_hat = np.dot(np.dot(K, S), u) + b

        z[l, M-1, :] = np.dot(np.squeeze(cholQinv[l, :, M-1, :]).transpose(), (y_meas[l, M-1, :].transpose() - y_hat))

    z=np.transpose(z, axes=(0, 2, 1))
    z = np.reshape(z, (3 *M * L, 1))
    z_list = []
    for i in range(0, len(z)):
        z_list.append(z[i][0])

    return z_list


# Does the least square approximation and estimates the parameters
def MIMU_calib_param_est(meas, M, C, scale_acc, scale_gyro, L, intMisalign, covW, covWFile,g):
    # Settings and memory allocation
    global y_meas
    global cholQinv
    global g_local
    g_local = g
    y_meas = np.zeros((L, M, 3), np.float64)             # Allocatememoryfor the measurements
    cholQinv = np.zeros((L, 3, M, 3), np.float64)        # Allocatememory for the noise covariance matrices
    theta = np.zeros((12, M), float)
    y_cal_mean = np.zeros((L, M, 3), float)
    gyro_mean = np.zeros((M, 3), float)

    # Load and preprocess the data
    # Loop through the data recorded at the L different orientations and take
    # the arithmetic mean of the data.  Estimate the noise covariance also.

    if covW: # only if covariance weighing is true. but its always false so far
        print "load(covWFile)",covWFile
        print "LOAD"


    for l in range(0, L):
        # Convert to double precision
        inertial_data = meas[l]
        for m in range(0, M):
            R = np.reshape(C[m, 0:9], (3, 3))
            tmp = scale_acc * np.dot(R, inertial_data[6*m:(6*m) + 3, :])
            y_meas[l, m, :] = np.mean(tmp, 1)
            npm = np.mean(scale_gyro * np.dot(R, inertial_data[6 * m + 3:6 * m + 6,:]), 1).transpose()/ L
            gyro_mean[m, :] += npm
            if covW:
                # To do in next release
                print "in inf covW"

            else:
                # Estimate the noise covariance of the m:th IMU at the l:th orientation
                a = lin.cholesky(lin.inv(np.cov(tmp))).transpose()
                cholQinv[l, :, m, :]= a.T


    y_meas[:, 0, :], y_meas[:, M-1, :] = y_meas[:, M-1, :].copy(), y_meas[:, 0, :].copy()
    cholQinv[:, :, 0, :], cholQinv[:, :, M-1, :] = cholQinv[:, :, M-1, :].copy(), cholQinv[:, :, 0, :].copy()

    # Calculate the initial estimates for the roll and pitch
    tmp = np.zeros((2, L), float)
    for l in range(0, L):
        # Calculate the mean over all IMUs.
        f = np.mean(y_meas[l, :, :], 0).transpose()

        # Roll
        tmp[0, l] = np.arctan2(f[1], f[2])

        # Pitch
        tmp[1, l] = np.arctan2(-f[0], pow(f[1]**2 + f[2]**2, 0.5))

    # Run estimation of the accelerometer scalefactors, biases, and IMU misalignment
    if intMisalign:
        # Define the initial state estimate
        temp = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        temp = np.reshape(temp, (len(temp), 1))
        theta0 = np.vstack((np.reshape(tmp, (2*L, 1), 1), np.tile(temp, (M, 1))))

        # Remove alignment parameters of last IMU
        theta0 = theta0[0:len(theta0) - 3]
        t = []
        for i in range(0, len(theta0)):
            t.append(theta0[i][0])
        theta0 = t

        # Run the optimazation
        myarray = np.asarray(theta0)
        tmp = least_squares(costFunctionArrayInternalMisalignment, myarray,method='lm',ftol=1e-6, gtol=1e-6, xtol=1e-6,verbose=2)
        print "Done"

        # Trow away the nuisance parameters, reinsert zeros for alignment of
        # last IMU, and reshape parameters into original form
        tmp = np.reshape(tmp.x, (len(tmp.x), 1))
        a=np.append(tmp[2 * L:, ], [0.0,0.0,0.0])
        theta[:, :] = np.reshape(a, (12, M), 1)


    else: #not needed internal misalignment is so far always true. maybe developed in future
        temp = np.array([1, 1, 1,  0, 0, 0,  0, 0, 0, ])
        temp = temp.transpose()
        theta0 = np.vstack((np.reshape(tmp, (2 * L, 1)), np.tile(temp, (M, 1))))
        theta0 = theta0[0:len(theta0) - 3]
        # Run the optimazation
        # tmp = least_squares(costFunctionArray, theta0)
        # Trow away the nuisance parameters, reinsert zeros for alignment of
        # last IMU, and reshape parameters into original form
        tmp = np.reshape(np.vstack((tmp[2*L:], np.zeros((3, 1), float))), (9, M))
        # Insert zeros for internal misalignment
        theta[:, :]=np.vstack((tmp[0:6, :], np.zeros((3, M), float), tmp[6:9, :]))

    # Calibrate the (time) mean value of the data at each orientation
    for m in range(0, M):
        theta_tmp = theta[:, m]
        # Set the calibration parameters
        K = np.diag(theta_tmp[0:3])
        S = np.eye(3)
        S[0, 1] = -theta_tmp[6]
        S[0, 2] = theta_tmp[7]
        S[1, 2] = -theta_tmp[8]
        b = theta_tmp[3:6]
        # TODO b=b(:);
        E = np.eye(3)
        E[0, 1] = theta_tmp[11]
        E[0, 2] = -theta_tmp[10]
        E[1, 0] = -theta_tmp[11]
        E[1, 2] = theta_tmp[9]
        E[2, 0] = theta_tmp[10]
        E[2, 1] = -theta_tmp[9]

        # Calibrate the accelerometers and the misalignment
        for l in range(0, L):

            tmp = np.squeeze(y_meas[l, m, :]) - b  # xyz = zxy
            tmp = np.reshape(tmp, (len(tmp), 1))

            y_cal_mean[l, m, :] = list(np.linalg.solve(np.dot(np.dot(K, S), E), tmp))

    # Switch back order of data (see switch after loading of data)

    theta = theta.transpose()
    theta[0, :], theta[M-1, :] = theta[M-1, :].copy(), theta[0, :].copy()

    #  Append gyro mean (biases) values
    theta = np.hstack((theta, gyro_mean))

    y_cal_mean[:, 0, :], y_cal_mean[:, M - 1, :] = y_cal_mean[:, M-1, :].copy(), y_cal_mean[:, 0, :].copy()

    return theta, y_cal_mean


