# github_actions_gcp
Github actions for source code updates/patches to google cloud resources like cloud functions.

This is currently only supported for Google Cloud Functions V2, but it is intended to expand to other versions and resources.

## Prerequisites for the parent repo using this Action

1. Setup the SECRETS in the repo before using this GitHub Action
   1. GCP_PROJECT
   2. GCP_REGION
   3. CLOUD_FUNCTION_NAME (the function that needs to be patched)
   4. SOURCE_CODE_DIRECTORY (the directory in your repo that needs to be pushed as source code)
   5. CREDENTIALS
2. CREDENTIALS expects a service account with the following roles:
   1. roles/cloudfunctions.developer
   2. roles/iam.serviceAccountUser for the particular cloud function runtime service account (more information at https://cloud.google.com/functions/docs/reference/iam/roles#additional-configuration.)
3. Don't add external quotes when saving CREDENTIALS secret, however it's recommended to replace double quotes with single quotes (following python code snippet might be useful)

```python
import json
service_acc = "<copy the dict from downloaded key from Google Cloud>"
# only required information are: client_email, token_uri, private_key. The rest of the dict items could be removed 
a = json.dumps(service_acc)
print(str(a).replace('\"', "\'"))
```


## Usage of this GitHub Action

If you have a repo with Cloud Function V2 source code and want to have CI, this action can help.

You can use this action using a workflow like this:

```yaml
name: patch-cloud-function
on: [push]

jobs:
  patch-cloud-function:
    runs-on: ubuntu-latest
    name: Pushes the source code into Google Cloud Storage and Patches a Cloud Function with source code update.
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Push Source Code to Cloud Storage and Patch the cloud function
        id: print_env_vars
        uses: KChaitanyaP/github_actions_gcp@v1.6   # update to use the latest version
        with:
          gcp_project: ${{ secrets.GCP_PROJECT }}
          gcp_region: ${{ secrets.GCP_REGION }}
          cloud_function_name: ${{ secrets.CLOUD_FUNCTION_NAME }}
          source_code_directory: ${{ secrets.SOURCE_CODE_DIRECTORY }}
          credentials: ${{ secrets.CREDENTIALS }}
```




