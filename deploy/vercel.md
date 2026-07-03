# Vercel Frontend Deployment

Deploy `frontend/` as the Vercel project root.

Required variables:

- `NEXT_PUBLIC_API_BASE_URL`: public backend URL.
- `NEXT_PUBLIC_APP_NAME`: `Enterprise Multi-Tool Agent Platform`.

Do not configure model provider secrets in Vercel `NEXT_PUBLIC_*` variables. Provider calls must go through the backend.
