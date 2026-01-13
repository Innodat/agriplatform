
# 1) Make a tiny test file
printf 'hello' > /tmp/test.txt

# 2) PUT the test file to your SAS URL (note required header x-ms-blob-type)
curl -v -X PUT \
  -H "x-ms-blob-type: BlockBlob" \
  -H "Content-Type: text/plain" \
  --data-binary @/tmp/test.txt \
  "https://liseliblob.blob.core.windows.net/content-liseli-dev/receipts/b3e3daa2-a4bb-411f-b7bb-9dd63cbb0f95/77a6389e-f27d-4590-9997-42eca997d8c3.jpeg?sv=2025-11-05&spr=https&st=2026-01-13T15%3A42%3A41Z&se=2026-01-13T16%3A12%3A41Z&sr=b&sp=cw&sig=fT956d%2FK71O%2BGAm3BHse5JKscYxWrgDNOj5H9%2F1hFBI%3D"
