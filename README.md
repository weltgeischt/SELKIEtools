
<p align="left">
<img src="images/logoSelkie.png" alt="SPOOChunter logo" width="400">
</p>

# SELKIE-tools

**S**wim **E**quipment **L**over's **K**omparative **I**nterval **E**valuation tools.

Preprocess, annotate and visualize your swim data.

Allows you to e.g. find the toy with which you swim fastest.


See [EXAMPLE](EXAMPLE.md) for a walkthrough

## Installation

```bash

git clone https://github.com/weltgeischt/SELKIEtools.git #download from github

cd SELKIEtools #navigate to toolbox

#create virtual environment (recommended):
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

#install
pip install -e . #this installs the selkie command and all dependencies
```


Set up your settings file once, if you don't want to repeat them each time:

```bash
cp SETTINGS/PATHS/general_paths.example.yml SETTINGS/PATHS/general_paths.yml 
# then edit general_paths.yml to point at your own config/output locations
```

```bash
export CSV=/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/src/cow/activity_24766304204.csv   
```



```bash
selkie process_csv $CSV -session_id KH241021 -N_cond 4
#--> creates session_id__processed.xlsx in outdir specified in paths (if not further specified outifle)
```

```bash
selkie plot_session KH241021 -debug
#--> creates session_id__processed.xlsx in outdir specified in paths (if not further specified outifle)
```



## Commands

<!-- COMMANDS:START -->
<!-- COMMANDS:END -->


## Saving and naming of figures produced

Files generated are by default named `<nwbstem>__<suffix>` and saved in the
`outdir` local `SETTINGS/PATHS/general_paths.yml` (not committed;
see [general_paths.example.yml](SETTINGS/PATHS/general_paths.example.yml) for
the expected structure, and [Installation](#installation) for how to set
yours up). You can override this on a per-call basis with the `-outdir` option and by
passing a full path instead of a tag to as an option (e.g.
`ecetools plot_spectrum /path/to/nwbfile.nwb -lfpfile /custom/path/x.h5`). This overrides the default, but loses the
ability to refer to that file by tag in later steps.

For this reason, it's recommended to run the pipeline with default settings
and copy files to their desired final locations only after processing with
ecephys_toolbox is complete. See [File tags](#file-tags) for the full list of
suffixes and what produces them.

**Naming example:** if your original nwb file is called `minnie261005-probe3.nwb`,
then `<nwbstem>` is `minnie261005-probe3`, and the resulting extracted LFP file
would be named `minnie261005-probe3__lfp.h5`.



## Config files

<!-- CONFIGS:START -->
<!-- CONFIGS:END -->


## Notes on usage


## Getting help

Details on what the script does, what options are available, and how to enter things?

```bash
ecetools <command> -h   
```


## Developer TODO

- [ ] Integrate visualization script from Runmaroe
- [ ] Make database with paddles, subjects, sessions
- [ ] Make multi-session/user evaluation