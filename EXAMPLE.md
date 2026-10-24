# Full example. From csv to visualization.
 
This walks through an entire pipeline on a real recording, from raw NWB to
extracted transients and annoted time epochs.
 
## 0.1 Install Setup
 
```bash
# cerate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
 
# install (editable — picks up code changes immediately)
cd SELKIEtools
pip install -e .
``` 

## 0.2 Define shell variables 

... so we don't retype long paths.

```bash
export NWB=/media/weltgeischt/ODIN/SPOOCs/toolbox_example/external_files/nwb_files/156131_20191112-probe0.nwb
export FLAGTIMES=/media/weltgeischt/ODIN/SPOOCs/toolbox_example/external_files/flagged_csvs/156131_20191112-probe0__flaggedtimes.csv
``` 
 
> These are plain shell variables — the shell substitutes `$NWB` before
> `ecetools` runs, so this works in any command below. They are not read
> automatically by ecetools; pass them explicitly each time, as shown.
 
## 1. Extract, resample, and denoise LFP
 
```bash
ecetools extract_lfp $NWB #extracts and resamples according to config file
# -> 156131_20191112-probe0__lfp.h5 in default outdir*
 
ecetools dehum_lfp $NWB
# -> 156131_20191112-probe0__lfpDehum.h5 in default outdir* and figuers if plot_on=1 (default) showing effect of denoising
```

*default outdir: see [Saving and naming of files produced](README.md#Saving-and-naming-of-files-produced)
 
To **inspect the denoising effect**, look at the figures created by `ecetools ehum_lfp`, which show the spectrum of a few channels
before and after denoising for random selected time epochs. In addition, you can plot the spectrum of all channels
in randomly selected time epochs by calling:

```bash
ecetools plot_spectrum $NWB -lfpfile lfp #plots spectra for the original lfp created by "ecetools extract_lfp"
# -> creates folder with figures to inspect

ecetools plot_spectrum $NWB -lfpfile lfp_dehum #plots spectra for the denoised lfp
# -> creates folder with figures to inspect

```

After inspecting and comparing the figures, you can decide which LFP to use for further analyses and 
set the `-lfpfile` option in the following calls accordingly.
 
## 2. Artifacts
 
**2.1:** write artifacts already known from the NWB into LFP files

```bash
# 
ecetools write_artifacts_orig $NWB -f lfp -f lfp_dehum
# --> creates dataset flagged_times/original_artifacts in the specified lfpfiles
```

**2.2:** manually mark additional artifacts using a GUI. Recommended to run on the ORIGINAL lfp, not dehummed.

```bash
ecetools set_artifacts_gui $NWB -lfpfile lfp
# -> 156131_20191112-probe0__lfpArtifactsGUI.h5
```

**2.3:** write those manually detected artifacts into both LFP files

```bash
ecetools write_artifacts_gui $NWB -f lfp -f lfp_dehum
# --> creates dataset flagged_times/manual_artifacts in the specified lfpfiles
```
 


## 3. Offstates


**3.1:** Detect offstates from cortical firing:
```bash
ecetools detect_offstates $NWB -X $FLAGTIMES #offstate detection does not happen during flagged times (passed by -X $FLAGTIMES) 
# -> 156131_20191112-probe0__offstates.h5
 ```
 
**3.2:** Plot offstates detected from cortical firing. If setting `-lfpfile` spectral characteristics during offstates will also be shown:
```bash
ecetools plot_offstates $NWB -lfpfile lfp_dehum -X $FLAGTIMES
# -> creates folder with figures to inspect
```


**3.3:** Inspect offstate plots and decide whether you trust that the offstates detected reflect genuine offstates. 
You might have doubts, e.g. if your recording contains only very few cortical units or if activity does not look
like genuine offstates (up/down activity during offstate blocks), e.g. because the subject might have been awake.
`-usable 1`: offstates are usable; `-usable 0`: you doubt that what was detected are actual offstates.

```bash
ecetools set_usable_offstates offstates -usable 1 -f lfp -f lfp_dehum
```
 
## 4. Transients
 
```bash
ecetools detect_transients $NWB lfp_dehum -prestopstim air_puff -X $FLAGTIMES1 --outdir $OUTDIR
# -> 156131_20191112-probe0__transients.h5
 
ecetools plot_trans_off $NWB lfp_dehum -X $FLAGTIMES1 --outdir $OUTDIR
# inspect: are offstate and transient detection trustworthy?
```
 
## 5. Spectra (optional, any time after step 1)
 
```bash
ecetools plot_spectrum lfp_dehum -cmap viridis --outdir $OUTDIR
```
 
## 6. Remaining steps (TODO — fill in once confirmed)
 
```bash
# ecetools write_transients transients -f lfp -f lfp_dehum --outdir $OUTDIR
# ecetools usable_to_csv ...
```
 
See the [Commands](README.md#commands) and [File tags](README.md#file-tags)
tables in the README for the full reference.
