# linkedin-job-scraper
linkedin job scraper

### installation
```
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
```

### create moggodb index
```
python src/linkedin.py --create-index
```

### drop mongodb index
```
python src/linkedin.py --drop-index
```

### crawl
```
python src/linkedin.py --crawl --write
```
