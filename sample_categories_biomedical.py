# sample_categories_biomedical.py

"""
Sample configuration focusing on biomedical research areas.
This configuration is tailored for analyzing grants in medical and biological sciences.
"""

GRANT_CATEGORIES = {
    'Research_Areas': {
        'Immunology': {
            'keywords': [
                'immune', 'immunity', 'immunological', 'antibody',
                'lymphocyte', 'inflammation'
            ],
            'subtypes': {
                'Autoimmune': [
                    'autoimmune', 'lupus', 'rheumatoid',
                    'multiple sclerosis', 'type 1 diabetes'
                ],
                'Vaccine_Development': [
                    'vaccine', 'immunization', 'adjuvant',
                    'immune response', 'antibody production'
                ],
                'Cancer_Immunology': [
                    'immunotherapy', 'checkpoint inhibitor',
                    'car-t', 'tumor immunity'
                ]
            }
        },
        'Genetics': {
            'keywords': [
                'genetic', 'genomic', 'dna', 'rna',
                'chromosome', 'mutation'
            ],
            'subtypes': {
                'Gene_Therapy': [
                    'gene therapy', 'gene editing', 'crispr',
                    'viral vector', 'gene delivery'
                ],
                'Rare_Diseases': [
                    'rare disease', 'genetic disorder',
                    'inherited disease', 'orphan disease'
                ],
                'Population_Genetics': [
                    'population genetics', 'genetic epidemiology',
                    'genetic variation', 'polymorphism'
                ]
            }
        },
        'Drug_Development': {
            'keywords': [
                'drug', 'therapeutic', 'pharmaceutical',
                'medicine', 'treatment'
            ],
            'subtypes': {
                'Small_Molecules': [
                    'small molecule', 'drug screening',
                    'medicinal chemistry', 'drug design'
                ],
                'Biologics': [
                    'biologics', 'monoclonal antibody',
                    'protein therapy', 'cell therapy'
                ],
                'Drug_Delivery': [
                    'drug delivery', 'formulation',
                    'bioavailability', 'pharmacokinetics'
                ]
            }
        }
    },

    'Technology_Platform': {
        'Molecular_Biology': {
            'keywords': [
                'pcr', 'sequencing', 'cloning',
                'molecular biology', 'gene expression'
            ],
            'subtypes': {
                'NGS': ['next generation sequencing', 'rna-seq', 'dna-seq'],
                'PCR_Methods': ['qpcr', 'rt-pcr', 'digital pcr'],
                'Cloning': ['molecular cloning', 'gene cloning']
            }
        },
        'Cell_Biology': {
            'keywords': [
                'cell culture', 'microscopy', 'flow cytometry',
                'cell biology'
            ],
            'subtypes': {
                'Microscopy': ['confocal', 'electron microscopy', 'fluorescence'],
                'Cell_Analysis': ['flow cytometry', 'cell sorting', 'facs'],
                'Culture': ['cell culture', 'tissue culture', 'organoid']
            }
        }
    },

    'Study_Design': {
        'Clinical_Trial_Phase': {
            'Phase1': ['phase 1', 'phase i', 'first in human'],
            'Phase2': ['phase 2', 'phase ii', 'proof of concept'],
            'Phase3': ['phase 3', 'phase iii', 'pivotal'],
            'Phase4': ['phase 4', 'phase iv', 'post-market']
        },
        'Study_Type': {
            'Basic_Research': ['basic science', 'fundamental research'],
            'Translational': ['translational', 'bench to bedside'],
            'Clinical': ['clinical study', 'patient study']
        }
    },

    'Award_Size': {
        'Small': {'max_amount': 250000},
        'Medium': {'min_amount': 250000, 'max_amount': 1000000},
        'Large': {'min_amount': 1000000}
    }
}

PROCESSING_CONFIG = {
    'text_processing': {
        'min_abstract_length': 100,               # Minimum abstract length to consider
        'max_abstract_length': 10000,             # Maximum abstract length to process
        'remove_stopwords': True,                 # Whether to remove common words
        'apply_stemming': True                    # Whether to apply word stemming
    },
    
    'similarity_thresholds': {
        'high': 0.8,                             # Threshold for high similarity
        'medium': 0.6,                           # Threshold for medium similarity
        'low': 0.4                               # Threshold for low similarity
    },
    
    'funding_ranges': {
        'very_small': 50000,
        'small': 200000,
        'medium': 1000000,
        'large': 5000000
    },
    
    'date_ranges': {
        'recent': 2,  # Years
        'medium_term': 5,
        'long_term': 10
    }
}