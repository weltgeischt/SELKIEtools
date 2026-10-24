'''Describes the tagged output files selkie scripts read/write'''

FILES = {
    'csv_fromGarmin': {
        'suffix': '.csv',
        'produced_by': 'user',
        'description': 'Exported Garmin splits.',
    },

    'processed': {
        'suffix': 'processed.xlsx',
        'produced_by': 'process_csv',
        'description': 'Table with processed splits, the basis for user annotation and further analyses.',
    }
}



# tag -> suffix only, for pathfns.resolve_file()'s lookup logic
SUFFIXES = {tag: info['suffix'] for tag, info in FILES.items()}