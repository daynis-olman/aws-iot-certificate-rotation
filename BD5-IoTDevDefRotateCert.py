import boto3
import json

client = boto3.client('iot')
data_client = boto3.client('iot-data')

def lambda_handler(event, context):
    #print(event)

    if "packageName" in event:
        if event["packageName"] == "DEVICE_CERTIFICATE_EXPIRING_CHECK":
            myThingName = event["ThingName"]
            cert_response = client.create_certificate_from_csr(
                certificateSigningRequest = event["csr"],
                setAsActive=True
            )

            myCertResponse = {}
            myCertResponse["JobId"] = event["JobId"]
            myCertResponse["certificateArn"] = cert_response["certificateArn"]
            myCertResponse["certificateId"] = cert_response["certificateId"]
            myCertResponse["certificatePem"] = cert_response["certificatePem"]
            print (cert_response["certificateArn"])

            #attach policy to certificate
            response = client.attach_policy(
                policyName='LabIoTDevicePolicy',
                target=cert_response["certificateArn"]
            )

            #attach thing/device to this certificate
            response = client.attach_thing_principal(
                thingName=myThingName,
                principal=cert_response["certificateArn"]
            )

            #send the new certificate back to the device
            data_client.publish(
                topic="res/"+ myThingName +"/jobs/",
                qos=0,
                payload=json.dumps(myCertResponse)
            )

    return 'Done'
