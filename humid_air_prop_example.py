# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 12:05:27 2014

@author: nfette
"""

#import the things you need
from CoolProp.HumidAirProp import HAProps, HAProps_Aux

#Enthalpy (kJ per kg dry air) as a function of temperature, pressure,
#    and relative humidity at dry bulb temperature T of 25C, pressure
#    P of one atmosphere, relative humidity R of 50%
h=HAProps('H','T',298.15,'P',101.325,'R',0.5); print h
# 50.4249283433

#Temperature of saturated air at the previous enthalpy
T=HAProps('T','P',101.325,'H',h,'R',1.0); print T
# 290.962168888

#Temperature of saturated air - order of inputs doesn't matter
T=HAProps('T','H',h,'R',1.0,'P',101.325); print T
# 290.962168888
