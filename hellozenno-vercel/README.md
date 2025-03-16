# Flask Hello World on Vercel

A minimal Flask application deployed as a serverless function on Vercel.

## Local Development

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the application:
```
python api/index.py
```

The app will be available at http://localhost:5000

## Deployment to Vercel

1. Install Vercel CLI:
```
npm install -g vercel
```

2. Login to Vercel:
```
vercel login
```

3. Deploy to Vercel:
```
vercel
```

4. For production deployment:
```
vercel --prod
``` 