from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import os
import time
from dotenv import load_dotenv

# Explicitly specify the .env file location
load_dotenv(dotenv_path=".env")

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

# Validate that credentials are loaded
if not endpoint or not key:
    raise ValueError("Azure credentials (endpoint and key) are not set in the environment variables.")

# Initialize the Computer Vision Client
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(endpoint=endpoint, credentials=credentials)

def read_image(uri):
    try:
        numberOfCharsInOperationId = 36
        maxRetries = 10

        print(f"Sending image URI to Azure: {uri}")
        rawHttpResponse = client.read(uri, language="en", raw=True)

        operationLocation = rawHttpResponse.headers["Operation-Location"]
        operationId = operationLocation[-numberOfCharsInOperationId:]

        retry = 0
        while retry < maxRetries:
            result = client.get_read_result(operationId)
            print(f"Polling result: {result.status}")

            if result.status.lower() not in ['notstarted', 'running']:
                break

            time.sleep(1)
            retry += 1

        if retry == maxRetries:
            print("Max retries reached.")
            return ""

        if result.status == OperationStatusCodes.succeeded:
            extracted_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
            print(f"Extracted text: {extracted_text}")
            return extracted_text
        else:
            print("Azure API processing failed.")
            return ""

    except Exception as e:
        print(f"Error in read_image: {e}")
        return ""
