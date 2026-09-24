"""Read-only Supabase bucket readiness check, using deployment-only administration."""
import os
import httpx

def main():
    key=os.environ['SUPABASE_STORAGE_ADMIN_KEY']
    response=httpx.get(os.environ['SUPABASE_URL'].rstrip('/')+'/storage/v1/bucket/'+os.environ['CONTENT_BUCKET'],headers={'Authorization':'Bearer '+key,'apikey':key},timeout=10)
    response.raise_for_status();bucket=response.json()
    if bucket.get('public') is not False:raise SystemExit('Content bucket must be private')
    maximum=bucket.get('file_size_limit')
    if maximum is not None and int(maximum)<134217728:raise SystemExit('Bucket size limit must allow 128 MiB')
    print('Bucket private and configured size ceiling sufficient. Verify global size limit and S3 expiry/immutability before activation.')

if __name__=='__main__':main()
