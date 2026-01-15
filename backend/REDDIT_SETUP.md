# Reddit API Setup Guide

## Why You Need This

The backend needs Reddit API credentials to fetch posts from Reddit. Without valid credentials, you'll get a **401 Unauthorized** error.

## Step-by-Step Setup

### 1. Create a Reddit Account (if you don't have one)
- Go to https://www.reddit.com
- Sign up for a free account

### 2. Create a Reddit App

1. **Go to Reddit Apps Page**
   - Visit: https://www.reddit.com/prefs/apps
   - Log in if prompted

2. **Create New App**
   - Scroll to the bottom
   - Click **"create another app..."** or **"create app"**

3. **Fill in the Form**
   ```
   name: viral-story-search
   App type: ● script (select this option)
   description: (leave blank or add description)
   about url: (leave blank)
   redirect uri: http://localhost:8000
   ```

4. **Click "create app"**

### 3. Get Your Credentials

After creating the app, you'll see something like this:

```
viral-story-search                    [edit] [delete]
personal use script
abc123XYZ456                          ← This is your CLIENT_ID
                                         (the string under "personal use script")

secret: xyz789ABC123def456            ← This is your CLIENT_SECRET
```

### 4. Update Your .env File

1. **Open** `backend/.env`

2. **Replace** the placeholder values:
   ```env
   REDDIT_CLIENT_ID=abc123XYZ456
   REDDIT_CLIENT_SECRET=xyz789ABC123def456
   REDDIT_USER_AGENT=viral-story-search/1.0
   ```

3. **Save** the file

### 5. Restart the Backend

If the backend is running, restart it:

```bash
# Stop the current process (Ctrl+C)
# Then restart from project root:
npm run dev
```

## Troubleshooting

### Error: "Reddit authentication failed: 401"

**Cause**: Invalid or missing credentials

**Solution**:
1. Double-check your CLIENT_ID and CLIENT_SECRET in `.env`
2. Make sure there are no extra spaces or quotes
3. Verify the app type is "script" (not "web app")
4. Try creating a new Reddit app if the issue persists

### Error: "Rate limit exceeded"

**Cause**: Too many requests to Reddit API

**Solution**:
- Wait 1-2 minutes before trying again
- Reddit has rate limits for API access
- The backend caches results to minimize API calls

### Error: "Invalid subreddit"

**Cause**: Subreddit doesn't exist or is private

**Solution**:
- Check the subreddit name spelling
- Try a popular subreddit like "AmItheAsshole" or "tifu"
- Private subreddits cannot be accessed via API

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit your `.env` file to Git
- Never share your CLIENT_SECRET publicly
- The `.env` file is already in `.gitignore`

## Testing Your Setup

Once configured, test the API:

```bash
# Start the backend
npm run dev

# In another terminal, test the health endpoint:
curl http://localhost:8000/health

# Test a search (should return results):
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["AmItheAsshole"],
    "time_range": "1d",
    "post_count": 5
  }'
```

If you see JSON results with posts, your setup is working! 🎉

## Need Help?

- Reddit API Documentation: https://www.reddit.com/dev/api
- Reddit Apps Page: https://www.reddit.com/prefs/apps
- Check backend logs for detailed error messages
