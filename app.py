from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

def load_csv_data():
    """Load and return the CSV data"""
    try:
        csv_path = os.path.join('static', 'data.csv')
        df = pd.read_csv(csv_path)
        
        # Clean column names - remove extra spaces and handle common variations
        df.columns = df.columns.str.strip()
        
        # Handle common column name variations
        column_mapping = {
            'Rank Category': ['Rank Category', 'RankCategory', 'Rank_Category'],
            'Category': ['Category', 'Quota', 'Seat Type'],
            'Closing Rank': ['Closing Rank', 'Closing_Rank', 'ClosingRank', 'Close Rank'],
            'Opening Rank': ['Opening Rank', 'Opening_Rank', 'OpeningRank', 'Open Rank'],
            'Institute': ['Institute', 'College', 'Institution'],
            'Branch': ['Branch', 'Course', 'Program'],
            'Gender': ['Gender', 'Pool']
        }
        
        # Rename columns to standard names
        for standard_name, variations in column_mapping.items():
            for variation in variations:
                if variation in df.columns:
                    df = df.rename(columns={variation: standard_name})
                    break
        
        print(f"Debug: Loaded CSV with columns: {list(df.columns)}")
        print(f"Debug: Total rows: {len(df)}")
        
        return df
    except FileNotFoundError:
        print("Error: data.csv not found in static folder")
        return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def filter_data(df, user_rank, category, rank_type, institute_preferences=None):
    """Filter data based on user inputs"""
    print(f"Debug: Input - user_rank: {user_rank}, category: {category}, rank_type: {rank_type}")
    print(f"Debug: Total records in CSV: {len(df)}")
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Clean data values (remove extra spaces)
    for col in ['Category', 'Rank Category', 'Institute', 'Branch']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    print(f"Debug: Available categories: {df['Category'].unique()}")
    print(f"Debug: Available rank types: {df['Rank Category'].unique()}")
    
    # Filter by category and rank type
    filtered_df = df[
        (df['Category'].str.upper() == category.upper()) & 
        (df['Rank Category'].str.upper() == rank_type.upper())
    ]
    
    print(f"Debug: After category/rank filter: {len(filtered_df)} records")
    
    # Filter by institute preferences if provided
    if institute_preferences:
        institute_list = [inst.strip() for inst in institute_preferences.split(',')]
        filtered_df = filtered_df[filtered_df['Institute'].isin(institute_list)]
        print(f"Debug: After institute filter: {len(filtered_df)} records")
    
    # Convert closing rank to numeric, handling any string values
    filtered_df = filtered_df.copy()
    filtered_df['Closing Rank'] = pd.to_numeric(filtered_df['Closing Rank'], errors='coerce')
    
    # Remove rows where Closing Rank is NaN
    filtered_df = filtered_df.dropna(subset=['Closing Rank'])
    
    print(f"Debug: After numeric conversion: {len(filtered_df)} records")
    print(f"Debug: Closing rank range: {filtered_df['Closing Rank'].min()} - {filtered_df['Closing Rank'].max()}")
    
    # Filter where closing rank >= user rank (user is eligible)
    eligible_df = filtered_df[filtered_df['Closing Rank'] >= user_rank]
    
    print(f"Debug: Final eligible records: {len(eligible_df)}")
    
    # Sort by closing rank (ascending)
    if len(eligible_df) > 0:
        eligible_df = eligible_df.sort_values('Closing Rank')
    
    return eligible_df

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/get_categories')
def get_categories():
    """Get unique categories from CSV"""
    df = load_csv_data()
    if df is not None:
        categories = sorted(df['Category'].unique().tolist())
        return jsonify({'categories': categories})
    return jsonify({'categories': []})

@app.route('/get_institutes')
def get_institutes():
    """Get unique institutes from CSV"""
    df = load_csv_data()
    if df is not None:
        institutes = sorted(df['Institute'].unique().tolist())
        return jsonify({'institutes': institutes})
    return jsonify({'institutes': []})

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.get_json()
        
        # Extract user inputs
        user_rank = int(data.get('crl_rank'))
        category = data.get('category')
        rank_type = data.get('rank_type', 'AI')  # Default to AI
        institute_preferences = data.get('institute_preferences', '').strip()
        
        # Load CSV data
        df = load_csv_data()
        if df is None:
            return jsonify({
                'success': False, 
                'error': 'Could not load data. Please ensure data.csv exists in static folder.'
            })
        
        # Filter data
        if not institute_preferences:
            institute_preferences = None
            
        eligible_df = filter_data(df, user_rank, category, rank_type, institute_preferences)
        
        # Convert to list of dictionaries
        results = []
        for _, row in eligible_df.iterrows():
            results.append({
                'institute': row['Institute'],
                'branch': row['Branch'],
                'category': row['Category'],
                'gender': row['Gender'],
                'opening_rank': int(row['Opening Rank']),
                'closing_rank': int(row['Closing Rank']),
                'rank_difference': int(row['Closing Rank']) - user_rank
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_options': len(results)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Please enter a valid rank (numbers only)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/stats')
def get_stats():
    """Get basic statistics about the data"""
    try:
        df = load_csv_data()
        if df is None:
            return jsonify({'error': 'Could not load data'})
        
        stats = {
            'total_entries': len(df),
            'unique_institutes': len(df['Institute'].unique()),
            'unique_branches': len(df['Branch'].unique()),
            'categories': df['Category'].unique().tolist(),
            'rank_range': {
                'min_opening': int(df['Opening Rank'].min()),
                'max_closing': int(df['Closing Rank'].max())
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Error getting stats: {str(e)}'})

@app.route('/debug')
def debug_data():
    """Debug endpoint to check data format"""
    try:
        df = load_csv_data()
        if df is None:
            return jsonify({'error': 'Could not load CSV'})
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        debug_info = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'categories': sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else [],
            'rank_types': sorted(df['Rank Category'].unique().tolist()) if 'Rank Category' in df.columns else [],
            'institutes': sorted(df['Institute'].unique().tolist()[:10]) if 'Institute' in df.columns else [],  # First 10
            'sample_data': df.head(3).to_dict('records'),
            'closing_rank_stats': {
                'min': int(df['Closing Rank'].min()) if 'Closing Rank' in df.columns else None,
                'max': int(df['Closing Rank'].max()) if 'Closing Rank' in df.columns else None,
                'data_type': str(df['Closing Rank'].dtype) if 'Closing Rank' in df.columns else None
            }
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': f'Debug error: {str(e)}'})

@app.route('/test_filter')
def test_filter():
    """Test filtering with sample data"""
    try:
        df = load_csv_data()
        if df is None:
            return jsonify({'error': 'Could not load CSV'})
        
        # Test with common values
        test_rank = 1000
        test_category = 'OPEN'  # Most common category
        test_rank_type = 'AI'
        
        result_df = filter_data(df, test_rank, test_category, test_rank_type)
        
        return jsonify({
            'test_parameters': {
                'rank': test_rank,
                'category': test_category,
                'rank_type': test_rank_type
            },
            'results_found': len(result_df),
            'sample_results': result_df.head(5).to_dict('records') if len(result_df) > 0 else []
        })
        
    except Exception as e:
        return jsonify({'error': f'Test error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)