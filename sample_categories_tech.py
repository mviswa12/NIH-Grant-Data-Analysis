# sample_categories_tech.py

"""
Sample configuration focusing on technology and computational research areas.
This configuration is tailored for analyzing grants in technology, data science,
and computational research domains.
"""

GRANT_CATEGORIES = {
    'Research_Areas': {
        'Artificial_Intelligence': {
            'keywords': [
                'artificial intelligence', 'ai', 'machine learning',
                'deep learning', 'neural network', 'intelligent system'
            ],
            'subtypes': {
                'Deep_Learning': [
                    'deep learning', 'neural network', 'cnn', 'rnn',
                    'transformer', 'deep neural', 'bert', 'gpt'
                ],
                'Natural_Language_Processing': [
                    'nlp', 'natural language', 'text mining', 'language model',
                    'text analysis', 'sentiment analysis', 'named entity'
                ],
                'Computer_Vision': [
                    'computer vision', 'image analysis', 'object detection',
                    'image recognition', 'visual processing', 'image segmentation'
                ],
                'Reinforcement_Learning': [
                    'reinforcement learning', 'rl', 'deep rl', 'policy learning',
                    'reward optimization', 'agent learning'
                ]
            }
        },
        'Data_Science': {
            'keywords': [
                'data science', 'big data', 'data analysis',
                'analytics', 'statistical analysis', 'data mining'
            ],
            'subtypes': {
                'Bioinformatics': [
                    'bioinformatics', 'computational biology',
                    'genomic data', 'biological data', 'sequence analysis'
                ],
                'Data_Mining': [
                    'data mining', 'pattern recognition', 'feature extraction',
                    'clustering', 'anomaly detection', 'association rules'
                ],
                'Predictive_Analytics': [
                    'predictive model', 'forecasting', 'prediction algorithm',
                    'statistical modeling', 'time series analysis'
                ],
                'Big_Data_Processing': [
                    'big data', 'data processing', 'data pipeline',
                    'data engineering', 'distributed processing'
                ]
            }
        },
        'Software_Systems': {
            'keywords': [
                'software', 'system architecture', 'distributed systems',
                'cloud computing', 'parallel computing'
            ],
            'subtypes': {
                'Cloud_Computing': [
                    'cloud platform', 'aws', 'azure', 'cloud native',
                    'cloud infrastructure', 'serverless'
                ],
                'Distributed_Systems': [
                    'distributed computing', 'microservices', 'containerization',
                    'kubernetes', 'docker', 'service mesh'
                ],
                'High_Performance_Computing': [
                    'hpc', 'supercomputing', 'parallel processing',
                    'gpu computing', 'cluster computing'
                ]
            }
        },
        'Cybersecurity': {
            'keywords': [
                'cybersecurity', 'security', 'privacy', 'cryptography',
                'network security', 'information security'
            ],
            'subtypes': {
                'Network_Security': [
                    'network security', 'firewall', 'intrusion detection',
                    'network monitoring', 'security protocol'
                ],
                'Cryptography': [
                    'cryptography', 'encryption', 'blockchain',
                    'cryptographic protocol', 'secure communication'
                ],
                'Privacy': [
                    'privacy preserving', 'anonymization', 'data privacy',
                    'differential privacy', 'privacy protection'
                ]
            }
        }
    },

    'Technology_Platform': {
        'Development_Tools': {
            'keywords': [
                'development platform', 'programming tool', 'ide',
                'development framework', 'software tools'
            ],
            'subtypes': {
                'Programming_Languages': ['python', 'java', 'c++', 'javascript'],
                'Frameworks': ['tensorflow', 'pytorch', 'react', 'django'],
                'Development_Environments': ['ide', 'jupyter', 'visual studio']
            }
        },
        'Infrastructure': {
            'keywords': [
                'infrastructure', 'platform', 'system architecture',
                'computing infrastructure', 'technical infrastructure'
            ],
            'subtypes': {
                'Cloud_Services': ['aws', 'azure', 'gcp', 'cloud services'],
                'Computing_Resources': ['gpu', 'cpu', 'computing cluster'],
                'Storage_Systems': ['database', 'data warehouse', 'data lake']
            }
        }
    },

    'Study_Design': {
        'Development_Phase': {
            'Research': ['research phase', 'investigation', 'exploration'],
            'Prototype': ['prototype', 'proof of concept', 'mvp'],
            'Development': ['development', 'implementation', 'construction'],
            'Testing': ['testing', 'validation', 'evaluation']
        },
        'Study_Type': {
            'Algorithm_Development': [
                'algorithm development', 'method development',
                'technique development'
            ],
            'System_Implementation': [
                'system implementation', 'software development',
                'platform development'
            ],
            'Empirical_Study': [
                'empirical study', 'experimental study',
                'comparative analysis'
            ]
        }
    },

    'Award_Size': {
        'Small': {'max_amount': 200000},
        'Medium': {'min_amount': 200000, 'max_amount': 750000},
        'Large': {'min_amount': 750000}
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
        'medium': 750000,
        'large': 2000000
    },
    
    'date_ranges': {
        'recent': 2,  # Years
        'medium_term': 5,
        'long_term': 10
    }
}