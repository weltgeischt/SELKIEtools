"""Source of truth: command name -> script path, what it produces, and what it requires.

`produces`/`requires` use file-tag names from file_registry.FILES where the
item is a tracked output file (so update_readme.py can cross-link them);
otherwise they're free text.
"""

SCRIPTS = {
    'process_csv': {
        'path': 'scripts/preprocess_raw.py',
        'produces': 'processed',
        'requires': 'csv_fromGarmin',
    },

    'plot_session': {
        'path': 'scripts/plot_session.py',
        'produces': 'figures',
        'requires': 'processed (user-edited for blocks and conditions)',
    },

}