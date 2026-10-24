"""config tag -> filename (in SETTINGS/config), description, and which commands read it."""

CONFIGS = {

    'sheetspec': {
        'filename': 'sheetspec.yml',
        'description': 'Parameters for setting up sheets of processed csv.',
        'used_by': ['process_csv'],
    },

    'headENG': {
        'filename': 'header_conversionENG.yml',
        'description': 'Converts English Garmin export headers to table headers.',
        'used_by': ['process_csv']
    },

    'headSWE': {
        'filename': 'header_conversionSWE.yml',
        'description': 'Converts Swedish Garmin export headers to table headers.',
        'used_by': ['process_csv']
    },

}