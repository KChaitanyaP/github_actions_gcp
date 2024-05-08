import json
import os
import zipfile
from tempfile import TemporaryFile
import requests
from google.oauth2 import service_account
from googleapiclient import discovery
from requests import Response
import time


def _zip_directory(handler, code_location):
    for root, dirs, files in os.walk(code_location):  # type: ignore # noqa: B007
        print("zipping these files: ")
        for file in files:
            print(file)
            handler.write(
                os.path.join(root, file),  # type: ignore
                os.path.relpath(
                    os.path.join(root, file), os.path.join(code_location, ".")  # type: ignore
                ),
            )


def _get_credentials():
    credentials = os.environ.get("CREDENTIALS")
    svc = json.loads(credentials.replace("\'", "\""))
    return service_account.Credentials.from_service_account_info(svc)


def _upload_source_code_using_upload_url(upload_url: str, data):
    # Prepare Header and data for PUT request
    # https://cloud.google.com/functions/docs/reference/rest/v1/projects.locations.functions/generateUploadUrl
    headers = {
        "content-type": "application/zip"
    }
    response: Response = requests.put(upload_url, headers=headers, data=data)
    print(f"HTTP Status Code for uploading data: {response.status_code} \n")
    print(f"Response body: {response.json} \n")


def _deploy():
    gcp_project = os.environ.get("GCP_PROJECT")
    gcp_region = os.environ.get("GCP_REGION")
    cloud_function_name = os.environ.get("CLOUD_FUNCTION_NAME")
    source_code_location = os.environ.get("SOURCE_CODE_DIRECTORY")

    parent = f"projects/{gcp_project}/locations/{gcp_region}"
    function_path = f"projects/{gcp_project}/locations/{gcp_region}/functions/{cloud_function_name}"

    service = discovery.build(
        "cloudfunctions", "v2", credentials=_get_credentials()
    )
    # noqa https://googleapis.github.io/google-api-python-client/docs/dyn/cloudfunctions_v2.projects.locations.operations.html#get
    cloud_functions = service.projects().locations().functions()
    function = cloud_functions.get(name=function_path).execute()
    # TODO add code to check if function is present or not
    with TemporaryFile() as data:
        file_handler = zipfile.ZipFile(data, mode="w")
        _zip_directory(file_handler, source_code_location)
        file_handler.close()
        data.seek(0)

        generate_upload_url_response = cloud_functions.generateUploadUrl(
            parent=parent, body={}
        ).execute()
        _upload_url = generate_upload_url_response['uploadUrl']
        _storage_source = generate_upload_url_response['storageSource']
        _upload_source_code_using_upload_url(_upload_url, data)
        function['buildConfig']['source']['storageSource']['bucket'] = _storage_source["bucket"]
        function['buildConfig']['source']['storageSource']['object'] = _storage_source["object"]

    response = cloud_functions.patch(name=function_path, body=function).execute()
    operation_name = response['name']
    print(f"checking the Source code update operation: {operation_name}")
    operation_details = service.projects().locations().operations().get(name=operation_name).execute()

    max_iterations = 30
    iteration_count = 0
    while iteration_count < max_iterations and not operation_details['done']:
        iteration_count += 1
        print(f"Iteration {iteration_count}: Waiting for 10 sec to get response from Google Cloud update_function...")
        time.sleep(10)
        operation_details = service.projects().locations().operations().get(name=operation_name).execute()

    if operation_details['done']:
        if 'response' in operation_details.keys():
            print(f"Source code update operation completed. response: {operation_details['response']}")
        elif 'error' in operation_details.keys():
            print(f"Seems some error in uploading source code. {operation_details['error']}")
            raise RuntimeError()
        else:
            print(f"Not sure whether Source Code is uploaded. Obtained Operation response: {operation_details}")
            raise NotImplementedError()
    else:
        print(f"Waited in total for 5 minutes but operation isn't complete in "
              f"Google Cloud for Update Function request. "
              f"Check the console after some time. {operation_details}")

    # TODO add messaging to Slack/Teams on the status


if __name__ == "__main__":
    _deploy()
