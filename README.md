# heating-device

This is an user-interface software for a heating device, allowing the communication between the PC and the heater. The hardware acts to hold at a constant setpoint the temperature in a thermal blanket by using a PID controller. More info about the hardware and technical specifications can be found in the microcontroller source file.

![Screenshot](screenshot.png)

By clicking in 'Pair', you start the communication and allow the software to receive the temperature data. It will be shown in the plot. The setpoint is automatically set to 20°C. Increase it to turn on the heating.

By clicking in the Settings push-button, you can adjust the PID parameters and the max/min temperature. These specifications will be saved and automatically loaded when the software opens again.

-------------------------------------------------------------------------------------------
Created by Allison Pessoa (allisonpessoa@hotmail.com) for academic purposes.

Please contact me to report misfunctions.
