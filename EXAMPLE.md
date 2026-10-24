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
