# vendor_ci

This is a small flask application to act as a relay between external users of apache/tvm's CI and GitHub/S3. GitHub is used to display results about CI runs to users, and S3 is used to store and serve logs with details about CI runs. Third parties can register with the maintainer of this application and get a username and API key. These can then be used to submit statuses on commits under apache/tvm for commits on the `nightly` branch only.

# Routes

## `/upload`

Submit a CI run for a commit on a PR or branch. This route must recieve a mutlipart request with a file called `log` and a JSON blob called `data` with the following structure:

```json
{
    "sha": "<a git sha>",
    "status": "<pending|success|failed>",
    "description": "<a short text description>"
}
```

Example usage with `curl`:

```bash
echo '
some long job log
' > log.txt
export USERNAME=test-ci
export API_KEY=tvm_q8ba1o1yxj9780v2vtfo0f2xmubivf
export GIT_SHA=3e3dd32a92547689bb2ac4e566e75f867f9d0a49
curl -X POST -H "Content-Type: multipart/form-data" \
    -H "Authorization: $USERNAME:$API_KEY" \
    -F "log=@log.txt" \
    -F "data={\"sha\": \"$GIT_SHA\", \"status\": \"pending\", \"description\": \"testing ci\"}" ci.tlcpack.ai:5000/upload
```