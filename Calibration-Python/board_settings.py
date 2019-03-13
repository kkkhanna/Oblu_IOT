# Function stores the settings for the sensor being calibrated.
# Gets the board from input.
# Returns command for raw data, matrix and number of IMUs
#     Date     |    Review    |      Author                      |  Comments
# -------------+--------------+-----------------------------------------------------
#   21-08-2016 |    0.0       |   Rahul Tiwari                   | Initial Release

import tkMessageBox as tk
import numpy as np

# Target board specific parameters
def b_settings(target_board, com):
    
    if target_board == 'OBLU':
        nr_imus = 4
        c_nom = [[1, 0, 0,  0, 1, 0,  0, 0, 1,  1, 0, 0,  0, 1, 0,  0, 0, 1],
                 [1, 0, 0,  0, 1, 0,  0, 0, 1,  1, 0, 0,  0, 1, 0,  0, 0, 1],
                 [1, 0, 0,  0, 1, 0,  0, 0, 1,  1, 0, 0,  0, 1, 0,  0, 0, 1],
                 [1, 0, 0,  0, 1, 0,  0, 0, 1, 1,  0, 0,  0, 1, 0,  0, 0, 1]]
        C_nom = np.reshape(c_nom, (4, 18))
        command = [40, 0, 0, 0, 15, 2+64, 0, 57+64] #USB
        return [nr_imus, C_nom, command]

    else:
        tk.showerror("Oops !", 'Target board not recognized. Aborting calibration')
        com.close()
        return [0,0,0]
