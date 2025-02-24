# run_analysis.py

from nih_data_fetcher import NIHDataFetcher
from analysis_pipeline import GrantAnalyzer
from category_handler import CategoryHandler
from categories_config import GRANT_CATEGORIES, PROCESSING_CONFIG
import pandas as pd
import sys
import time
from datetime import datetime
import traceback
import os

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'pandas', 
        'numpy', 
        'torch', 
        'transformers',
        'tqdm', 
        'plotly',
        'seaborn',
        'matplotlib',
        'openpyxl',
        'requests'
    ]
    
    print("Checking required packages...")
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    if missing_packages:
        print("\nMissing required packages. Please install:")
        for package in missing_packages:
            print(f"pip install {package}")
        sys.exit(1)

def create_output_directory():
    """Create directory for output files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"nih_analysis_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def print_analysis_summary(grants_df):
    """Print detailed analysis summary"""
    print("\nAnalysis Summary Report:")
    print("-" * 50)
    
    # Basic statistics
    print(f"Total grants processed: {len(grants_df)}")
    print(f"Total funding amount: ${grants_df['award_amount'].sum():,.2f}")
    print(f"Average award amount: ${grants_df['award_amount'].mean():,.2f}")
    
    # Duration distribution
    print("\nGrants by duration:")
    print(grants_df['project_duration_category'].value_counts())
    
    # Award size distribution
    print("\nGrants by award size:")
    print(grants_df['award_size_category'].value_counts())
    
    # Top organizations
    print("\nTop 5 organizations by number of grants:")
    print(grants_df['org_name'].value_counts().head())
    print("-" * 50)

def main():
    try:
        # Step 1: Check dependencies
        print("Starting NIH Grants Analysis Pipeline...")
        check_dependencies()
        
        # Step 2: Create output directory
        output_dir = create_output_directory()
        print(f"\nOutput directory created: {output_dir}")
        
        # Step 3: Initialize category handler
        print("\nInitializing category handler...")
        category_handler = CategoryHandler(GRANT_CATEGORIES)
        
        # Step 4: Initialize fetcher and analyzer
        print("\nInitializing NIH data fetcher...")
        fetcher = NIHDataFetcher(category_handler)
        
        # Step 5: Create search criteria
        print("\nCreating search criteria...")
        criteria = fetcher.create_search_criteria(
            fiscal_years=[2023, 2024],
            keywords=None  # We'll categorize later
        )
        
        # Step 6: Fetch data
        print("\nFetching data from NIH RePORTER...")
        projects = fetcher.fetch_data(criteria)
        
        if not projects:
            print("No projects found. Exiting...")
            return
        
        # Step 7: Process initial data
        print("\nProcessing fetched data...")
        grants_df = fetcher.process_projects(projects)
        
        # Save raw processed data
        raw_data_path = os.path.join(output_dir, 'raw_nih_grants.xlsx')
        print(f"\nSaving raw processed data to {raw_data_path}")
        fetcher.save_data(grants_df, raw_data_path)
        
        # Step 8: Initialize and run analyzer
        print("\nInitializing grant analyzer...")
        analyzer = GrantAnalyzer(category_handler)
        
        # Step 9: Process using both methods
        print("\nProcessing grants using regular method...")
        regular_results = analyzer.process_regular_method(grants_df)
        
        print("\nProcessing grants using SciBERT method...")
        scibert_embeddings = analyzer.process_scibert_method(grants_df)
        
        # Step 10: Calculate similarities
        print("\nCalculating similarities between grants...")
        regular_sims, scibert_sims = analyzer.calculate_similarities(
            regular_results, 
            scibert_embeddings
        )
        
        # Step 11: Create visualizations
        print("\nCreating visualizations...")
        analyzer.create_visualizations(
            grants_df,
            regular_results,
            scibert_sims
        )
        
        # Step 12: Save final results
        analysis_output_path = os.path.join(output_dir, 'nih_grants_analysis.xlsx')
        print(f"\nSaving final analysis results to {analysis_output_path}")
        analyzer.save_results(
            grants_df,
            regular_results,
            scibert_sims,
            analysis_output_path
        )
        
        # Step 13: Print summary
        print_analysis_summary(grants_df)
        
        # Step 14: Provide next steps guidance
        print("\nAnalysis complete!")
        print(f"\nFiles saved in: {output_dir}")
        print("\nFor Tableau visualization:")
        print("1. Use 'nih_grants_analysis.xlsx' as your primary data source")
        print("2. Key sheets for visualization:")
        print("   - Grants_Data: Main dataset with all categorizations")
        print("   - State_Analysis: Geographic distribution of grants")
        print("   - Category_Summary: Research area breakdowns")
        print("   - Method_Comparison: Analysis method comparisons")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("\nFull error trace:")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()