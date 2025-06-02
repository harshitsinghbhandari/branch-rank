# IIT Admission Predictor

A Flask web application that helps students predict their eligible IIT branches based on JEE Advanced ranks and cutoff data.

## Features

- **Rank-based Prediction**: Input your CRL rank to find eligible colleges
- **Category Filtering**: Filter by reservation categories (OPEN, SC, ST, etc.)
- **Institute Preferences**: Optionally filter by specific IIT preferences
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Results**: Dynamic filtering and sorting of results

## Project Structure

```
branch-rank/
├── app.py              # Flask backend application
├── templates/
│   └── index.html      # Frontend interface
├── static/
│   └── data.csv        # Cutoff data 
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone/Create Project

```bash
git clone https://github.com/harshitsinghbhandari/branch-rank.git
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`


## API Endpoints

- `GET /` - Main application page
- `GET /get_categories` - Get available categories
- `GET /get_institutes` - Get available institutes
- `POST /predict` - Get predictions based on input
- `GET /stats` - Get data statistics

## Troubleshooting

### Common Issues

1. **CSV not found**: Ensure `data.csv` is in the `static` folder
2. **Module not found**: Make sure all dependencies are installed
3. **Port already in use**: Change the port in `app.py` or kill the process using the port

### Data Format Issues

- Ensure column names match exactly
- Remove any extra spaces in headers
- Verify numeric columns contain valid numbers
- Check for missing values

### Performance Optimization

For large datasets:
- Consider using database instead of CSV
- Add caching for repeated queries
- Implement pagination for results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the CSV format requirements
3. Ensure all dependencies are installed correctly

---

**Note**: Remember to add your actual cutoff data in the `data.csv` file for the application to work properly.