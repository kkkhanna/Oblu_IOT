
def settings():  # Generates settings widget
    global open_settings
    if open_settings == 1:
        open_settings = 0

        r = Tkinter.Tk()
        r.withdraw()

        setting = Tkinter.Tk()  # New root for settings
        setting.title("Settings")  # Setting up the title
        setting.iconbitmap("icons/transparent.ico")
        setting.protocol("WM_DELETE_WINDOW", lambda: close_settings(setting))
        width = setting.winfo_screenwidth()  # getting the screen width
        height = setting.winfo_screenheight()  # getting the screen height
        setting.resizable(0, 0)
        setting.geometry('%dx%d+%d+%d' % (510, 300, width/2-205, (height - 40)/2-285))
        tframe = Frame(setting)  # Top frame containing g value, Accelerometer Range, Gyroscope Range,
        #                          port for setting, digits after decimal and x axis range
        tframe.pack(side=TOP)
        set_g = IntVar(setting)

        # **** Placing widgets in grid layout ****

        gval_lbl = Checkbutton(tframe, text="'g' value is", variable=set_g, onvalue=1, offvalue=0,
                               command=lambda: enable(set_g, gentry))
        gval_lbl.grid(row=3, sticky=W, pady=(20, 15))
        g_string = StringVar(tframe)
        g_string.set(str(gvalue))
        gentry = Entry(tframe, textvariable=g_string, state=DISABLED, width=10)
        gentry.grid(row=3, column=1, padx=(20, 0), pady=(20, 15), sticky=W)
        Label(tframe, text="m/s^2").grid(row=3, column=2, padx=(0, 120), sticky=W)

        gval_lbl = Checkbutton(tframe, text="'g' value \n(give the latitute and altitude)", variable=set_g, onvalue=1, offvalue=0,
                               command=lambda: enable(set_g, gentry))
        gval_lbl.grid(row=3, sticky=W, pady=(20, 15))
        g_string1 = StringVar(tframe)
        g_string1.set(str(g_lat))
        glat = Entry(tframe, textvariable=g_string1, state=DISABLED, width=5)
        glat.grid(row=3, column=1, padx=(20, 0),pady=(20, 15), sticky=W)
        Label(tframe, text="deg").grid(row=3, column=2, padx=(0, 20), sticky=W)
        g_string2 = StringVar(tframe)
        g_string2.set(str(g_alt))
        galt = Entry(tframe, textvariable=g_string2, state=DISABLED, width=5)
        galt.grid(row=3, column=3, padx=(20, 0), pady=(20, 15), sticky=W)

        misalign_lbl1 = Checkbutton(tframe, text="Internal Misalignment", variable=set_g, onvalue=1, offvalue=0,command=lambda: enable(set_g, gentry))
        misalign_lbl1.grid(row=4, sticky=W, pady=(20, 15))
        misalign = StringVar(tframe)
        misalign.set('True')
        misalign_option = ['True', 'False']
        misalign_box = Combobox(tframe, textvariable=misalign, values=misalign_option, state='readonly', height=5, width=8)
        misalign_box.grid(row=4, column=1, padx=(20, 0), pady=15, sticky=W)

        gval_lbl2 = Checkbutton(tframe, text="Covariance weighing", variable=set_g, onvalue=1, offvalue=0,command=lambda: enable(set_g, gentry))
        gval_lbl2.grid(row=5, sticky=W, pady=(20, 15))
        covar = StringVar(tframe)
        covar.set('False')
        misalign_option = ['True', 'False']
        covar_box = Combobox(tframe, textvariable=covar, values=misalign_option, state='readonly', height=5, width=8)
        covar_box.grid(row=5, column=1, padx=(20, 0), pady=15, sticky=W)

        gval_lbl3 = Checkbutton(tframe, text="Covariance weighing", variable=set_g, onvalue=1, offvalue=0,
                                command=lambda: enable(set_g, gentry))
        gval_lbl3.grid(row=6, sticky=W, pady=(20, 15))
        save = StringVar(tframe)
        save.set(str(save_loc))
        saveentry = Entry(tframe, textvariable=save, state=DISABLED, width=20)
        saveentry.grid(row=6, column=1,columnspan=8, padx=(20, 0), pady=(20,15), sticky=W)

        btnframe = Frame(setting)
        btnframe.pack(side=BOTTOM)
        apply_btn = Button(btnframe, text="Apply",
                           command=lambda: set(set_g, g_string, a_r_var, a_scale, g_r_var, g_scale,
                                               s_imu_var, s_imu_1, s_imu_2, s_imu_3, s_imu_4, cport,
                                               pointstring, x_r_var, y_r_var1, y_r_var2, y_r_var1g, y_r_var2g,
                                               c_file_var, setting))
        apply_btn.grid(row=0, pady=15)
        reset_btn = Button(btnframe, text="Reset values", command=lambda: reset(g_string, a_scale, g_scale, cport,
                                                                                pointstring, setting))
        reset_btn.grid(row=0, column=1, padx=(30, 0), pady=10)
        close_btn = Button(btnframe, text="Close", command=lambda: close_settings(setting))
        close_btn.grid(row=0, column=2, sticky=E, padx=(30, 0), pady=15)

        # **** Hover info of widgets in settings ****
        default_info = '\n No selection would pick default value programmed in sensor'
        info(gentry, 'Select to overwrite acceleration due to gravity' + default_info)
        info(apply_btn, ' All the settings would be effective')
        info(reset_btn, 'Display all the default values on this page')
        info(close_btn, ' Close the window')
        # done till this

        '''
        gval_lbl = Checkbutton(tframe, text="Internal Misalignment", variable=set_g, onvalue=1,offvalue=0,command=lambda: enable(set_g, gentry))
        gval_lbl.grid(row=4, sticky=W, pady=(20, 15))
        g_string = StringVar(tframe)
        g_string.set(str('True'))
        gentry = Entry(tframe, textvariable=g_string, values=misalign_option, state='readonly', width=5)
        gentry.grid(row=4, column=1, padx=(20, 0), pady=(20, 15), sticky=W)
        #Label(tframe, text="deg").grid(row=4, column=2, padx=(0, 20), sticky=W)'''

        a_scale = StringVar(setting)
        g_scale = StringVar(setting)
        a_scale.set(ascale)
        g_scale.set(gscale)
        accelo_range = ['+/-2', '+/-4', '+/-8', '+/-16']
        gyro_range = ['+/-250', '+/-500', '+/-1000', '+/-2000']
        points_range = ['1', '2', '3', '4', '5', '6']
        a_r_var = IntVar(setting)
        Checkbutton(tframe, text="Acclerometer Range ", variable=a_r_var, onvalue=1, offvalue=0,
                               command=lambda: enablechkbox(a_r_var, asclvalue)).grid(row=4, sticky=W)
        asclvalue = Combobox(tframe, textvariable=a_scale, values=accelo_range, height=5, state=DISABLED, width=8)
        asclvalue.grid(row=4, column=1, padx=(20, 0), sticky=W)
        Label(tframe, text=" g ").grid(row=4, column=2, sticky=W)
        g_r_var = IntVar(setting)
        Checkbutton(tframe, text="Gyroscope Range ", variable=g_r_var, onvalue=1, offvalue=0,
                               command=lambda: enablechkbox(g_r_var, gsclvalue)).grid(row=5, pady=15, sticky=W)
        gsclvalue = Combobox(tframe, textvariable=g_scale, values=gyro_range, height=5, state=DISABLED, width=8)
        gsclvalue.grid(row=5, column=1, padx=(20, 0), sticky=W)
        Label(tframe, text="degree/second").grid(row=5, column=2, sticky=W)
        s_imu_1 = IntVar(setting)
        s_imu_2 = IntVar(setting)
        s_imu_1.set(imu1)
        s_imu_2.set(imu2)
        imu_1 = Checkbutton(tframe, text="IMU 1", variable=s_imu_1, onvalue=1, offvalue=0, state=DISABLED)
        imu_1.grid(row=6, column=1)
        imu_2 = Checkbutton(tframe, text="IMU 2", variable=s_imu_2, onvalue=1, offvalue=0, state=DISABLED)
        imu_2.grid(row=6, column=2)
        s_imu_var = IntVar(setting)
        S_imu = Checkbutton(tframe, text="Select IMUs ", variable=s_imu_var, onvalue=1, offvalue=0,
                    command=lambda: enable_IMUs(s_imu_var, imu_1, imu_2, imu_3, imu_4))
        S_imu.grid(row=7, sticky=W)
        s_imu_3 = IntVar(setting)
        s_imu_4 = IntVar(setting)
        s_imu_3.set(imu3)
        s_imu_4.set(imu4)
        imu_3 = Checkbutton(tframe, text="IMU 3", variable=s_imu_3, onvalue=1, offvalue=0, state=DISABLED)
        imu_3.grid(row=8, column=1)
        imu_4 = Checkbutton(tframe, text="IMU 4", variable=s_imu_4, onvalue=1, offvalue=0, state=DISABLED)
        imu_4.grid(row=8, column=2)

        Label(tframe, text="Port for setting").grid(row=9,  sticky=W)
        cport = StringVar(setting)
        cport.set('Select')
        c_port_box = Combobox(tframe, textvariable=cport, values=ports, state='readonly', height=5, width=8)
        c_port_box.grid(row=9, column=1, padx=(20, 0), pady=15, sticky=W)

        #  set_pts = IntVar(setting)
        point_lbl = Label(tframe, text='Digits after decimal')
        point_lbl.grid(row=10, sticky=W, pady=(0, 15))
        pointstring = StringVar(setting)
        pointstring.set(get_file_value('data/points.txt'))
        pointentry = Combobox(tframe, textvariable=pointstring, values=points_range, state="readonly", height=4, width=8)
        pointentry.grid(row=10, column=1, padx=(20, 0), sticky=W,pady=(0, 15))
        Label(tframe, text="Graphical Display").grid(row=11, sticky=W, pady=(5, 15))
        Label(tframe, text="Time range (x)").grid(row=12, sticky=W, pady=(0, 15), padx=(20, 0))
        x_r_var = IntVar(setting)
        x_r_var.set(get_file_value('data/xaxis.txt'))
        x_range_entry = Entry(tframe, textvariable=x_r_var, width=11)
        x_range_entry.grid(row=12, column=1, padx=(20, 0), pady=(0, 15), sticky=W)
        Label(tframe, text="Seconds").grid(row=12, column=2, pady=(0, 15), sticky=W)

        y_r_frame = Frame(setting)  # Mid frame containing ,Y axis range for accelerometer
        #                             Y axis range for gyroscope
        y_r_frame.pack()

        # **** Placing widgets in grid layout ****
        Label(y_r_frame, text="Acceleration range (y)").grid(row=0, sticky=W, padx=(20, 20))
        y_r_var1 = StringVar(setting)
        y_r_var1.set(float(get_y_axis()[0]))
        y_range_entry1 = Entry(y_r_frame, textvariable=y_r_var1, width=4)
        y_range_entry1.grid(row=0, column=1, sticky=W)
        Label(y_r_frame, text="to").grid(row=0, column=2, sticky=W)
        y_r_var2 = StringVar(setting)

        y_r_var2.set(float(get_y_axis()[1]))
        y_range_entry2 = Entry(y_r_frame, textvariable=y_r_var2, width=4)
        y_range_entry2.grid(row=0, column=3, sticky=W)
        Label(y_r_frame, text="g").grid(row=0, column=4, sticky=W, padx=(0, 40))

        Label(y_r_frame, text="Angular rate range (y)").grid(row=1, sticky=W, padx=(20, 48), pady=(15, 0))
        y_r_var1g = IntVar(setting)
        y_r_var1g.set(float(get_y_axis()[2]))
        y_range_entry1g = Entry(y_r_frame, textvariable=y_r_var1g, width=4)
        y_range_entry1g.grid(row=1, column=1, sticky=W, pady=(15, 0))
        Label(y_r_frame, text="to").grid(row=1, column=2, pady=(15, 0), sticky=W)
        y_r_var2g = IntVar(setting)
        y_r_var2g.set(float(get_y_axis()[3]))
        y_range_entry2g = Entry(y_r_frame, textvariable=y_r_var2g, width=4)
        y_range_entry2g.grid(row=1, column=3, sticky=W, pady=(15, 0))
        Label(y_r_frame, text="degree/second").grid(row=1, column=4, sticky=W, padx=(0, 40), pady=(15, 0))
        rframe = Frame(setting)  # bottom frame containing default directory and calibration file
        rframe.pack(side=TOP)

        # **** Placing widgets in grid layout ****
        dir_lbl = Label(rframe, text="Default Directory ")
        dir_lbl.grid(row=1, column=0, sticky=W, padx=(10, 0), pady=(20, 15))
        dirvar = StringVar(setting)
        dirvar.set(get_file_value('data/directory.txt'))
        dir_entry=Entry(rframe, textvariable=dirvar,state="readonly", width=30)
        dir_entry.grid(row=1, column=1, columnspan=2, sticky=W, pady=(20, 15))
        dir_btn = Button(rframe, text="Browse", command=lambda: changedir(dirvar))
        dir_btn.grid(row=1, padx=(10, 20), column=3, sticky=W, pady=(20, 15))
        c_file_var = IntVar(setting)
        cali_label = Checkbutton(rframe, text="Calibration file ", variable=c_file_var, onvalue=1, offvalue=0,
                               command=lambda: enable_entry(c_file_var, cfileentry, cali_btn))
        cali_label.grid(row=2, column=0, padx=(10, 0), sticky=W)
        califilevar = StringVar(setting)
        califilevar.set(califile )  # get_file_value('califile.txt'))
        cfileentry = Entry(rframe, textvariable=califilevar, width=30,state=DISABLED)
        cfileentry.grid(row=2, column=1, columnspan=2, sticky=W)
        cali_btn = Button(rframe, text="Browse", state=DISABLED, command=lambda: set_califile(califilevar))
        cali_btn.grid(row=2, column=3, padx=(10, 20), sticky=W)
        btnframe = Frame(setting)
        btnframe.pack(side=BOTTOM)
        apply_btn = Button(btnframe, text="Apply", command=lambda: set(set_g,g_string,a_r_var, a_scale,g_r_var, g_scale,
                                                        s_imu_var, s_imu_1, s_imu_2, s_imu_3, s_imu_4, cport,
                                                        pointstring, x_r_var, y_r_var1, y_r_var2, y_r_var1g, y_r_var2g,
                                                        c_file_var, setting))
        apply_btn.grid(row=0,pady=15)
        reset_btn = Button(btnframe, text="Reset values", command=lambda: reset(g_string, a_scale, g_scale, cport,
                                                                                pointstring, setting))
        reset_btn.grid(row=0, column=1, padx=(30, 0), pady=10)
        close_btn = Button(btnframe, text="Close", command=lambda: close_settings(setting))
        close_btn.grid(row=0, column=2, sticky=E, padx=(30, 0), pady=15)

        # **** Hover info of widgets in settings ****
        default_info = '\n No selection would pick default value programmed in sensor'
        info(dir_btn, 'Click to change the default directory')
        info(cali_btn, 'Click to upload the calibration file')
        info(gentry, 'Select to overwrite acceleration due to gravity' + default_info)
        info(asclvalue, "Select to change accelerometer's range" + default_info)
        info(gsclvalue, "Select to change gyroscope's range" + default_info)
        info(S_imu, 'Select to choose active IMUs\n Possible combinations - any 1 active IMU, any 2 active IMUs and all'
                    ' 4 active IMUs \n All 4 active IMUs, if not selected')
        info(c_port_box, 'Select serial port for communicate settings')
        info(pointentry, 'Select number of digits after decimal for log file format')
        info(dir_entry, 'Set default directory for log files')
        info(cfileentry, 'Select calibration input file for overwriting existing values' + default_info)
        info(apply_btn, ' All the settings would be effective')
        info(reset_btn, 'Display all the default values on this page')
        info(close_btn, ' Close the window')
        setting.mainloop()
    else:
        tkMessageBox.showerror("Oops ! :( ",setting_message)


