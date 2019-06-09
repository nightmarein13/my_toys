Most copy from rhf1d

in */rh15d/io.h*

add variable `ray_flux_var` in `/* for the ray file */`
used to keep flux variable ID

in *writeRay.c*

in line 166, after `/* Attach dimension scales */` add
```c
 /* Radiation Flux */
 if (( io.ray_flux_var = H5Dcreate(ncid, FLUX_NAME, H5T_NATIVE_FLOAT,
                                    file_dspace, H5P_DEFAULT, plist,
                                    H5P_DEFAULT)) < 0) HERR(routineName);
 /* Attach dimension scales */
 if (( H5DSattach_scale(io.ray_flux_var, id_x, 0)) < 0) HERR(routineName);
 if (( H5DSattach_scale(io.ray_flux_var, id_y, 1)) < 0) HERR(routineName);
 if (( H5DSattach_scale(io.ray_flux_var, id_wave, 2)) < 0) HERR(routineName);
 ```

in `/* --- Open datasets collectively ---*/` add 
```c
if (( io.ray_flux_var = H5Dopen(ncid, FLUX_NAME, H5P_DEFAULT) ) < 0)
    HERR(routineName);
```

in `/* Close all datasets */` add
```c
if (( H5Dclose(io.ray_flux_var) ) < 0) HERR(routineName);
```

add variable `*flux`, `*wmuz` in double definition of `writeRay{void}; mu in int` definition

after `/* Write intensity */` procedure add
```c
/* Calculate the radiative flux in the z-dircetion */
wmuz = (double *) malloc(atmos.Nrays * sizeof(double));
for (mu = 0;  mu < atmos.Nrays;  mu++)
wmuz[mu] = geometry.muz[mu] * geometry.wmu[mu];
    
flux = (double *) calloc(spectrum.Nspect, sizeof(double));
for (nspect = 0;  nspect < spectrum.Nspect;  nspect++) {
    for (mu = 0;  mu < atmos.Nrays;  mu++)
    flux[nspect] += spectrum.I[nspect][mu] * wmuz[mu];
    flux[nspect] *= 2.0 * PI;
 }
  
 /* Write the radiative flux in the z-direction */
 if (( H5Dwrite(io.ray_flux_var, H5T_NATIVE_DOUBLE, mem_dataspace,
                 file_dataspace, H5P_DEFAULT, flux) ) < 0) HERR(routineName);
```
