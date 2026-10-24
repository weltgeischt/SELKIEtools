
<p align="left">
<img src="images/logoSelkie.png" alt="selkie logo" width="400">
</p>

# SELKIE-tools

**S**wim **E**quipment **L**over's **K**omparative **I**nterval **E**valuation tools.

Preprocess, annotate and visualize your swim data.

Allows you to e.g. identify the toy with which you swim fastest.


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



## 1. Preprocess csv Export

For a swim session, export the splits to csv from your Garmin page.
![export_csv_from_garmin.png](example_files/export_csv_from_garmin.png)


Preprocess this file with selkietools into an editable table.
Through the argument `N_cond` you specify the number of conditions used,
e.g. if you test 3 paddles you would put `-N_cond 3`. `sesssion_id` is the 
name by which you would like to refer to this session.


```bash
selkie process_csv /path/to/my/csvexport/activity_24766304204.csv  -session_id KH241021 -N_cond 4
```

This creates session_id__processed.xlsx in `outdir` as
specified in `SETTINGS/PATHS/general_paths.yml` (if not further specified outifle)


## 2. Annotate table

Please edit the following sheets of the created xlsx file:

**summary**
The sheet looks like this:
![summary_proc.png](example_files/summary_proc.png)

Each row corresponds to an interval. Please mark the blocks (column `block`) 
with unique ids and the conditions (column `cond`, resolved in sheet `cond_spec`)
with unique ids or letters. If an interval in a block is not usable, please replace `+`
with `-` in column `usable`.


Example of edited summary file:
![summary_edited.png](example_files/summary_edited.png)
In this example there were two blocks, one I called x1 and one x2. These are annoted in the
colum `block`.
In each block, I used four different paddles in a pyramid setup, starting with paddle A. 
The "paddle" in this case is the conditon (column `cond`)

**cond_spec**
The sheet looks like this:
![cond_spec_proc.png](example_files/cond_spec_proc.png)

Please enter what each condition (A,B,C,D) in this case means, and which
condition you would like to use as a reference to express the relative
performance of the other conditions. You can also change the colors
by which the different conditions will be visualized. The field `pref_rank` allows
you to rank the equipment conditions according to preference (rank 1 is best).  

Example of edited cond_spce sheet:
![cond_spec_edited.png](example_files/cond_spec_edited.png)

Here my conditions are paddles and the FspM is my reference paddle.

**metadata**
The sheet looks like this:

![metadata_proc.png](example_files/metadata_proc.png)

Example of edited metadata sheet:
![metadata_edited.png](example_files/metadata_edited.png)

## 3. Plot session data

```bash
selkie plot_session KH241021
```
This creates a folder with session visualizations. The folder is by default located
as specified in `SETTINGS/PATHS/general_paths.yml` 


## 4. Compare performance across sessions 



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