# Vercel Deployment Guide

1. Push your code to GitHub/GitLab/Bitbucket.
2. Go to https://vercel.com/import and import your repo.
3. Set environment variables in Vercel dashboard (see .env.example).
4. Vercel will auto-detect Next.js and deploy.
5. For custom domains, configure in Vercel dashboard.

## Notes
- Ensure your Supabase keys are set in Vercel environment settings.
- If you use serverless functions, place them in `/api`.
