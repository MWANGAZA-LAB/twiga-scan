# GitHub Pages 404 Fix - Single Page Application Routing

## Problem
When deploying a React SPA (Single Page Application) to GitHub Pages, direct navigation to routes (like `/scan` or `/history`) or page refreshes result in a 404 error. This happens because GitHub Pages doesn't have server-side configuration to redirect all routes to `index.html`.

## Solution Implemented

### 1. GitHub Pages Specific Files

#### `frontend/public/404.html`
- Custom 404 page that redirects to the main app
- Converts path segments into query parameters
- Uses `pathSegmentsToKeep = 1` for GitHub Pages project sites (not root domain)
- GitHub Pages serves this file for any 404 error

#### `frontend/public/index.html`
- Added redirect script that processes the query parameters
- Restores the original URL using `history.replaceState()`
- This creates a seamless client-side routing experience

#### `frontend/public/.nojekyll`
- Empty file that prevents Jekyll processing
- Ensures files starting with `_` are served correctly
- Required for proper React app deployment

### 2. Docker/Nginx Configuration (for self-hosted deployments)

#### `nginx-frontend.conf`
- Standalone nginx config for frontend container
- Uses `try_files $uri $uri/ /index.html` to handle client-side routing
- Caches static assets but not `index.html`
- Includes security headers

#### `Dockerfile.frontend`
- Updated to use `nginx-frontend.conf` instead of `nginx.conf`
- Ensures proper SPA routing in Docker containers

#### `nginx.prod.conf`
- Added `try_files` directive for production deployments
- Handles client-side routing when using reverse proxy

## How It Works

### GitHub Pages Flow:
1. User visits `https://mwangaza-lab.github.io/twiga-scan/scan`
2. GitHub Pages doesn't find `/scan` and serves `404.html`
3. `404.html` script converts URL to: `/?/scan`
4. Browser loads `index.html` with the query parameter
5. `index.html` script extracts `/scan` and updates browser history
6. React Router takes over and renders the correct component

### Docker/Nginx Flow:
1. User visits `http://localhost/scan`
2. Nginx tries to find `/scan` file (doesn't exist)
3. `try_files` directive serves `index.html` instead
4. React Router handles the `/scan` route client-side

## Testing

### GitHub Pages Deployment:
```bash
cd frontend
npm run build
npm run deploy
```

Then test:
- Navigate to main URL: `https://mwangaza-lab.github.io/twiga-scan`
- Click internal links (should work)
- Refresh the page (should no longer show 404)
- Share a direct link like `https://mwangaza-lab.github.io/twiga-scan/scan` (should work)

### Docker Deployment:
```bash
# Build and run
docker-compose up --build

# Test routes
curl http://localhost/
curl http://localhost/scan
curl http://localhost/history
```

All routes should return the same HTML (index.html) with HTTP 200, not 404.

## Important Notes

1. **pathSegmentsToKeep**: Set to `1` for GitHub Pages project sites (`username.github.io/repo-name`). Set to `0` for custom domains.

2. **Homepage in package.json**: Must match your GitHub Pages URL:
   ```json
   "homepage": "https://mwangaza-lab.github.io/twiga-scan"
   ```

3. **Browser History**: Uses `replaceState()` to maintain clean URLs without exposing the redirect mechanism.

4. **SEO Considerations**: This solution works for client-side rendering. For better SEO, consider:
   - Using React-Helmet for meta tags
   - Implementing server-side rendering (SSR)
   - Using a service that supports server-side redirects

## Files Modified

- ✅ `frontend/public/404.html` - Created (GitHub Pages redirect handler)
- ✅ `frontend/public/index.html` - Updated (URL restoration script)
- ✅ `frontend/public/.nojekyll` - Created (Disable Jekyll)
- ✅ `nginx-frontend.conf` - Created (SPA routing for Docker)
- ✅ `Dockerfile.frontend` - Updated (Use new nginx config)
- ✅ `nginx.prod.conf` - Updated (Added try_files for reverse proxy)

## References

- [spa-github-pages](https://github.com/rafgraph/spa-github-pages) - The redirect solution we implemented
- [Create React App - GitHub Pages](https://create-react-app.dev/docs/deployment/#github-pages)
- [Nginx try_files](http://nginx.org/en/docs/http/ngx_http_core_module.html#try_files)
