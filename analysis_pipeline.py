# analysis_pipeline.py

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from tqdm import tqdm

class GrantAnalyzer:
    def __init__(self, category_handler):
        """Initialize with category handler for dynamic category processing"""
        self.category_handler = category_handler
        print("Initializing SciBERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def process_regular_method(self, grants_df):
        """Process grants using regular keyword-based method with dynamic categories"""
        print("Processing grants using regular method...")
        results = pd.DataFrame()
        
        # Process Research Areas
        for area, details in self.category_handler.config['Research_Areas'].items():
            # Check both title and abstract
            results[f'is_{area}'] = grants_df.apply(
                lambda x: self.category_handler.check_text_for_category(
                    str(x['project_title']) + " " + str(x['abstract_text']),
                    area,
                    include_subtypes=False
                ),
                axis=1
            )
            
            # Process subtypes
            for subtype, keywords in details['subtypes'].items():
                results[f'is_{area}_{subtype}'] = grants_df.apply(
                    lambda x: any(
                        kw in str(x['project_title']).lower() or 
                        kw in str(x['abstract_text']).lower() 
                        for kw in keywords
                    ),
                    axis=1
                )

        # Process Technology Platforms
        for platform, config in self.category_handler.config['Technology_Platform'].items():
            results[f'uses_{platform}'] = grants_df.apply(
                lambda x: any(
                    kw in str(x['abstract_text']).lower() 
                    for kw in config['keywords']
                ),
                axis=1
            )

        # Process Study Designs
        for design_type, subtypes in self.category_handler.config['Study_Design'].items():
            for subtype, keywords in subtypes.items():
                results[f'study_design_{design_type}_{subtype}'] = grants_df.apply(
                    lambda x: any(
                        kw in str(x['abstract_text']).lower() 
                        for kw in keywords
                    ),
                    axis=1
                )

        return results

    def process_scibert_method(self, grants_df):
        """Process grants using SciBERT embeddings"""
        print("Processing grants using SciBERT method...")
        embeddings = []
        
        for abstract in tqdm(grants_df['abstract_text'], desc="Generating embeddings"):
            inputs = self.tokenizer(
                str(abstract),
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
                embeddings.append(embedding)
                
        return np.array(embeddings)

    def calculate_similarities(self, regular_results, scibert_embeddings):
        """Calculate similarities between grants using both methods"""
        print("Calculating similarities...")
        
        # Regular method similarities (using binary vectors)
        regular_vectors = regular_results.select_dtypes(include=['bool', 'int64']).values
        regular_similarities = cosine_similarity(regular_vectors)
        
        # SciBERT similarities
        scibert_similarities = cosine_similarity(scibert_embeddings)
        
        return regular_similarities, scibert_similarities

    def compare_methods_accuracy(self, grants_df, regular_results, scibert_sims):
        """Compare accuracy between regular and SciBERT methods"""
        print("Comparing method accuracies...")
        
        # Calculate basic metrics for both methods
        regular_metrics = {
            'Total_Categories': len(regular_results.columns),
            'Average_Categories_Per_Grant': regular_results.sum(axis=1).mean(),
            'Total_Positive_Classifications': regular_results.sum().sum()
        }
        
        scibert_metrics = {
            'High_Similarity_Pairs': (scibert_sims > 0.8).sum(),
            'Average_Similarity': scibert_sims.mean(),
            'Max_Similarity': scibert_sims.max()
        }
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame({
            'Method': ['Regular Method', 'SciBERT Method'],
            'Categories_Detected': [
                regular_metrics['Total_Categories'],
                scibert_metrics['High_Similarity_Pairs']
            ],
            'Average_Score': [
                regular_metrics['Average_Categories_Per_Grant'],
                scibert_metrics['Average_Similarity'] * 100
            ],
            'Total_Classifications': [
                regular_metrics['Total_Positive_Classifications'],
                scibert_metrics['High_Similarity_Pairs']
            ],
            'Processing_Type': ['Keyword-Based', 'AI-Based'],
            'Description': [
                'Based on predefined keywords and categories',
                'Based on semantic understanding of text'
            ]
        })
        
        return comparison_df

    def create_geographic_analysis(self, grants_df, regular_results):
        """Create detailed state-wise analysis"""
        print("Creating geographic analysis...")
        
        # Basic state metrics
        state_analysis = grants_df.groupby('org_state').agg({
            'award_amount': ['count', 'sum', 'mean', 'median'],
            'application_id': 'count'
        }).round(2)
        
        # Convert monetary values to millions
        for col in ['sum', 'mean', 'median']:
            state_analysis[('award_amount', col)] /= 1e6
        
        # Research area breakdowns by state
        for area in self.category_handler.config['Research_Areas'].keys():
            col = f'is_{area}'
            if col in regular_results.columns:
                state_analysis[f'{self.category_handler.clean_category_name(area)}_Grants'] = (
                    grants_df[regular_results[col]].groupby('org_state').size()
                )
        
        # Calculate funding percentages
        total_funding = grants_df['award_amount'].sum()
        state_analysis['Funding_Percentage'] = (
            state_analysis[('award_amount', 'sum')] * 1e6 / total_funding * 100
        ).round(2)
        
        return state_analysis

    def create_visualizations(self, grants_df, regular_results, scibert_sims):
        """Create enhanced visualizations"""
        print("Creating visualizations...")
        
        # 1. Research Area Distribution
        category_cols = self.category_handler.get_all_category_columns()
        research_dist = regular_results[category_cols].sum().sort_values(ascending=True)
        
        plt.figure(figsize=(15, 8))
        sns.barplot(
            x=research_dist.values,
            y=[self.category_handler.clean_category_name(col) for col in research_dist.index]
        )
        plt.title('Distribution of Grants by Research Area')
        plt.xlabel('Number of Grants')
        plt.ylabel('Research Area')
        plt.tight_layout()
        plt.savefig('research_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 2. State Funding Distribution
        state_funding = grants_df.groupby('org_state')['award_amount'].sum().sort_values(ascending=True)
        
        plt.figure(figsize=(15, 8))
        sns.barplot(x=state_funding.values/1e6, y=state_funding.index)
        plt.title('Total Funding by State')
        plt.xlabel('Funding Amount (Millions $)')
        plt.ylabel('State')
        plt.tight_layout()
        plt.savefig('state_funding.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 3. Methods Comparison
        comparison_df = self.compare_methods_accuracy(grants_df, regular_results, scibert_sims)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=comparison_df,
            x='Method',
            y='Average_Score'
        )
        plt.title('Method Comparison: Average Scores')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('method_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 4. Similarity Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(scibert_sims.flatten(), bins=50)
        plt.title('Distribution of SciBERT Similarity Scores')
        plt.xlabel('Similarity Score')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig('similarity_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 5. Interactive Timeline
        fig = px.timeline(
            grants_df,
            x_start='project_start_date',
            x_end='project_end_date',
            y='award_size_category',
            color='award_amount',
            title='Grant Timeline by Award Size',
            labels={
                'award_size_category': 'Award Size',
                'award_amount': 'Award Amount ($)'
            }
        )
        fig.write_html('grant_timeline.html')

    def save_results(self, grants_df, regular_results, scibert_sims, output_path):
        """Save enhanced results with comprehensive summary"""
        print(f"Saving results to {output_path}")
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 1. Main Data
                print("Processing and saving main data...")
                combined_df = pd.concat([grants_df, regular_results], axis=1)
                
                # Get boolean columns (categories)
                bool_columns = combined_df.select_dtypes(include=['bool']).columns
                
                # Drop columns where all values are False
                non_empty_cols = [col for col in bool_columns 
                                if combined_df[col].any()]
                
                # Convert remaining boolean columns to 0/1
                for col in non_empty_cols:
                    combined_df[col] = combined_df[col].astype(int)
                
                # Keep only non-empty category columns and all other columns
                other_cols = [col for col in combined_df.columns 
                            if col not in bool_columns]
                final_cols = other_cols + non_empty_cols
                
                # Save processed data
                combined_df[final_cols].to_excel(
                    writer, 
                    sheet_name='Grants_Data',
                    index=False
                )
                # 2. State Analysis
                print("Saving geographic analysis...")
                state_analysis = self.create_geographic_analysis(grants_df, regular_results)
                state_analysis.to_excel(writer, sheet_name='State_Analysis')
                
                # 3. Method Comparison
                print("Saving method comparison...")
                comparison_df = self.compare_methods_accuracy(
                    grants_df, regular_results, scibert_sims
                )
                comparison_df.to_excel(writer, sheet_name='Method_Comparison', index=False)
                
                # 4. Category Summary
                print("Creating category summary...")
                category_summary = pd.DataFrame({
                    'Category': non_empty_cols,
                    'True_Count': [combined_df[col].sum() for col in non_empty_cols],
                    'Percentage': [
                        f"{(combined_df[col].sum() / len(combined_df) * 100):.2f}%" 
                        for col in non_empty_cols
                    ]
                })
                category_summary.to_excel(
                    writer,
                    sheet_name='Category_Summary',
                    index=False
                )
                category_summary.to_excel(writer, sheet_name='Category_Summary', index=False)
                
                # 5. Overall Summary
                print("Saving overall summary...")
                summary_stats = {
                    'Overview': {
                        'Total Grants': len(grants_df),
                        'Total Funding': f"${grants_df['award_amount'].sum():,.2f}",
                        'Average Award': f"${grants_df['award_amount'].mean():,.2f}",
                        'SciBERT Average Similarity': f"{scibert_sims.mean():.3f}"
                    }
                }
                
                summary_rows = []
                for category, items in summary_stats.items():
                    summary_rows.append({'Category': category, 'Metric': '', 'Value': ''})
                    for metric, value in items.items():
                        summary_rows.append({'Category': '', 'Metric': metric, 'Value': value})
                
                pd.DataFrame(summary_rows).to_excel(
                    writer, 
                    sheet_name='Overall_Summary',
                    index=False
                )
                
            print("Results saved successfully!")
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            # Save as CSV as backup
            combined_df.to_csv(output_path.replace('.xlsx', '.csv'), index=False)
            print(f"Saved backup to CSV: {output_path.replace('.xlsx', '.csv')}")