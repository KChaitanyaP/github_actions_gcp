import os

gcp_project = os.environ.get("GCP_PROJECT")
gcp_region = os.environ.get("GCP_REGION")
cloud_function_name = os.environ.get("CLOUD_FUNCTION_NAME")
cloud_function_directory = os.environ.get("CLOUD_FUNCTION_DIRECTORY")
credentials = os.environ.get("CREDENTIALS")
debug_mode = os.environ.get("DEBUG_MODE")
token = os.environ.get("TOKEN")

# to set output, print to shell in following syntax
# print(f"::set-output name=num_squared::{num ** 2}")
print("gcp_project", gcp_project)
print("gcp_region", gcp_region)
print("cloud_function_name", cloud_function_name)
print("cloud_function_directory", cloud_function_directory)
print("credentials", credentials)
print("debug_mode", debug_mode)
print("token", token)
