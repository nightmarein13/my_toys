import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import rh15d
import ipywidgets.widgets as widgets
import h5py
from ipywidgets import interact, Button, Layout, HBox, FloatText
import scipy.interpolate as interp
    
def find_nearest_index(array,value):
    idx = (np.abs(array - value)).argmin()
    return idx

class EditAtmosphere:
    """
    Class to visualise the atmosphere and edit it 
    """ 

    def __init__(self,filename):
        self.atmos = h5py.File(filename,'a')
        self.electron_density = self.atmos['electron_density'][()]
        self.height = self.atmos['z'][()]
        self.temperature = self.atmos['temperature'][()]
        self.velocity_z = self.atmos['velocity_z'][()]
        self.turbulence = self.atmos['velocity_turbulent'][()]
        self.filename = filename
        self.index = 0
        self.axes = 0
        self.lns = 0
        self.edit_index = 0
        self.display()
    
    def display(self):

        ntsteps, nx, ny, nz = self.temperature.shape

        def _atmos_plot_init_():
            titles = (r'$T$ (K)',r'$n_e$ (m$^{-3}$)',r'$v_z$ (m/s)',r'$v_{\xi}$ (m/s)')
            fig,((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(10,6))

            
            ln1, = ax1.plot(self.height[0,self.index,0]/1e6,self.temperature[0,self.index,0])
            ln2, = ax2.plot(self.height[0,self.index,0]/1e6,self.electron_density[0,self.index,0])
            ln3, = ax3.plot(self.height[0,self.index,0]/1e6,self.velocity_z[0,self.index,0])
            ln4, = ax4.plot(self.height[0,self.index,0]/1e6,self.turbulence[0,self.index,0])

            self.time_text = ax1.text(0.05,0.2,r'',fontsize = 12,transform = ax1.transAxes)
            #self.time_text.set_text(str(self.height[0,0,0,0]))

            for i,ax_ in enumerate((ax1,ax2,ax3,ax4)):
                ax_.ticklabel_format(axis='y',style='sci',scilimits=(0,0)) 
                ax_.set_title(titles[i])
                ax_.grid(True)
            plt.show()
            self.axes = (ax1,ax2,ax3,ax4)
            self.lns = (ln1,ln2,ln3,ln4)       

        def _atmos_plot_update_data_():
            idx_min = find_nearest_index(self.height[0,self.index,0]/1e6,self.axes[0].get_xlim()[0])
            idx_max = find_nearest_index(self.height[0,self.index,0]/1e6,self.axes[0].get_xlim()[1])

            for i,quantity in enumerate((self.temperature,self.electron_density,
            self.velocity_z,self.turbulence)):
                self.lns[i].set_data(self.height[0,self.index,0]/1e6,quantity[0,self.index,0])
                quantity_min = quantity[0,self.index,0,idx_max:idx_min].min()
                quantity_max = quantity[0,self.index,0,idx_max:idx_min].max()
                self.axes[i].set_ylim(1.2*quantity_min-0.2*quantity_max,1.2*quantity_max-0.2*quantity_min)
            
            return 0
        
        def _atmos_index_update_(time_index=0):
            self.index = time_index
            _atmos_plot_update_data_()
        
        def _atmos_plot_update_height_min_(height_min=0):
            for ax_ in self.axes:
                ax_.set_xlim(height_min,ax_.get_xlim()[1])
            idx_min = find_nearest_index(self.height[0,self.index,0]/1e6,height_min)
            idx_max = find_nearest_index(self.height[0,self.index,0]/1e6,self.axes[0].get_xlim()[1])
            

            for i,quantity in enumerate((self.temperature,self.electron_density,
            self.velocity_z,self.turbulence)):
                quantity_min = quantity[0,self.index,0,idx_max:idx_min].min()
                quantity_max = quantity[0,self.index,0,idx_max:idx_min].max()
                self.axes[i].set_ylim(1.2*quantity_min-0.2*quantity_max,1.2*quantity_max-0.2*quantity_min)

        def _atmos_plot_update_height_max_(height_max=5):
            for ax_ in self.axes:
                ax_.set_xlim(ax_.get_xlim()[0],height_max)
            idx_min = find_nearest_index(self.height[0,self.index,0]/1e6,self.axes[0].get_xlim()[0])
            idx_max = find_nearest_index(self.height[0,self.index,0]/1e6,height_max)
            

            for i,quantity in enumerate((self.temperature,self.electron_density,
            self.velocity_z,self.turbulence)):
                quantity_min = quantity[0,self.index,0,idx_max:idx_min].min()
                quantity_max = quantity[0,self.index,0,idx_max:idx_min].max()
                self.axes[i].set_ylim(1.2*quantity_min-0.2*quantity_max,1.2*quantity_max-0.2*quantity_min)   

        def _atmos_edit_quantity_():
            if self.edit_index == 0:
                lower_height = text_lower_height.value*1e6
                lower_value = text_lower_value.value
                upper_height = text_upper_height.value*1e6
                upper_value = text_upper_value.value
                if lower_height == upper_height and lower_value == upper_value:
                    idx = find_nearest_index(self.height[0,self.index,0],lower_height)
                    self.temperature[0,self.index,0,idx] = lower_value
                else:
                    x = np.array([lower_height,upper_height])
                    y = np.array([lower_value,upper_value])
                    f = interp.interp1d(x,y)

                    idx_min = find_nearest_index(self.height[0,self.index,0],lower_height)
                    idx_max = find_nearest_index(self.height[0,self.index,0],upper_height)
                    height_select = self.height[0,self.index,0,idx_max+1:idx_min]

                    temperature_new = f(height_select)
                    self.temperature[0,self.index,0,idx_max+1:idx_min] = temperature_new

            if self.edit_index == 1:
                lower_height = text_lower_height.value*1e6
                lower_value = text_lower_value.value
                upper_height = text_upper_height.value*1e6
                upper_value = text_upper_value.value

                if lower_height == upper_height and lower_value == upper_value:
                    idx = find_nearest_index(self.height[0,self.index,0],lower_height)
                    self.electron_density[0,self.index,0,idx] = lower_value
                else:
                    x = np.array([lower_height,upper_height])
                    y = np.array([lower_value,upper_value])
                    f = interp.interp1d(x,y)

                    idx_min = find_nearest_index(self.height[0,self.index,0],lower_height)
                    idx_max = find_nearest_index(self.height[0,self.index,0],upper_height)
                    height_select = self.height[0,self.index,0,idx_max+1:idx_min]

                    electron_density_new = f(height_select)
                    self.electron_density[0,self.index,0,idx_max+1:idx_min] = electron_density_new

            if self.edit_index == 2:
                lower_height = text_lower_height.value*1e6
                lower_value = text_lower_value.value
                upper_height = text_upper_height.value*1e6
                upper_value = text_upper_value.value

                if lower_height == upper_height and lower_value == upper_value:
                    idx = find_nearest_index(self.height[0,self.index,0],lower_height)
                    self.velocity_z[0,self.index,0,idx] = lower_value
                else:
                    x = np.array([lower_height,upper_height])
                    y = np.array([lower_value,upper_value])
                    f = interp.interp1d(x,y)

                    idx_min = find_nearest_index(self.height[0,self.index,0],lower_height)
                    idx_max = find_nearest_index(self.height[0,self.index,0],upper_height)
                    height_select = self.height[0,self.index,0,idx_max+1:idx_min]

                    velocity_z_new = f(height_select)
                    self.velocity_z[0,self.index,0,idx_max+1:idx_min] = velocity_z_new

            if self.edit_index == 3:
                lower_height = text_lower_height.value*1e6
                lower_value = text_lower_value.value
                upper_height = text_upper_height.value*1e6
                upper_value = text_upper_value.value

                if lower_height == upper_height and lower_value == upper_value:
                    idx = find_nearest_index(self.height[0,self.index,0],lower_height)
                    self.turbulence[0,self.index,0,idx] = lower_value
                else:
                    x = np.array([lower_height,upper_height])
                    y = np.array([lower_value,upper_value])
                    f = interp.interp1d(x,y)

                    idx_min = find_nearest_index(self.height[0,self.index,0],lower_height)
                    idx_max = find_nearest_index(self.height[0,self.index,0],upper_height)
                    height_select = self.height[0,self.index,0,idx_max+1:idx_min]

                    turbulence_new = f(height_select)
                    self.turbulence[0,self.index,0,idx_max+1:idx_min] = turbulence_new


        def _atmos_edit_index_update_(edit_quantity=0):
            self.edit_index = edit_quantity
        
        def on_change_button_clicked(b):
            _atmos_edit_quantity_()
            _atmos_plot_update_data_()
            button_change.description = 'Change Again?'

        def on_save_button_clicked(b):
            self.atmos['electron_density'][()] = self.electron_density
            self.atmos['temperature'][()] = self.temperature
            self.atmos['velocity_z'][()] = self.velocity_z
            self.atmos['velocity_turbulent'][()] = self.turbulence
            button_save.description = 'Save Again?'

        def on_close_button_clicked(b):
            button_close_file.description = 'Already Closed!'
            self.atmos.close()
        
        _atmos_plot_init_() 

        interact(_atmos_index_update_,time_index=(0,nx-1,1))
     
        interact(_atmos_plot_update_height_min_,height_min = (0,10,0.02))

        interact(_atmos_plot_update_height_max_,height_max = (0,10,0.02))

        interact(_atmos_edit_index_update_,edit_quantity=[('temperature', 0), ('electron_density', 1),
        ('velocity_z',2),('turbulence',3)])

        text_lower_height = FloatText(description='lower_height',value=0,disabled=False)
        text_lower_value = FloatText(description='lower_value',value=0,disabled=False)
        text_upper_height = FloatText(description='upper_height',value=0,disabled=False)
        text_upper_value = FloatText(description='upper_value',value=0,disabled=False)
        display(HBox((text_lower_height,text_lower_value,text_upper_height,text_upper_value)))

        button_change = Button(description='Change!')
        button_change.on_click(on_change_button_clicked)

        button_save = Button(description='Save!',)
        button_save.on_click(on_save_button_clicked)

                
        button_close_file = Button(description='Close File')
        button_close_file.on_click(on_close_button_clicked)
        display(HBox((button_change,button_save,button_close_file)))

