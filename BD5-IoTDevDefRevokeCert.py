import boto3
import re
client = boto3.client('iot')

def lambda_handler(event, context):

    #get list of certs for this thing
    certsResponse = client.list_thing_principals(
        thingName = event["ThingName"]
    )

    #revoke and delete all certs associated with this thing except for the new one
    for certARN in certsResponse["principals"]:
        if certARN != event["certificateArn"]:
            #get cert id
            base,certificateId = certARN.split("/")

            #check its status
            statusResponse = client.describe_certificate(
                certificateId = certificateId
            )

            if statusResponse["certificateDescription"]["status"] != "REVOKED":
                #revoke the certificate
                updateCertResponse = client.update_certificate(
                    certificateId = certificateId,
                    newStatus = 'REVOKED'
                )
                print("Revoked cert: " + certificateId)

                #list the policies for the cert so they can be detached
                policiesResponse = client.list_attached_policies(
                    target=certARN,
                    recursive=False
                )

                #remove the attachement
                for policy in policiesResponse["policies"]:
                    response = client.detach_principal_policy(
                        policyName=policy["policyName"],
                        principal=certARN
                    )
                    print("Detached policy: " + policy["policyName"])

                #detach the cert from the thing
                response = client.detach_thing_principal(
                    thingName=event["ThingName"],
                    principal=certARN
                )

                #delete the certificate
                response = client.delete_certificate(
                    certificateId=certificateId,
                    forceDelete=False
                )
                print("Delete cert: " + certificateId)

    return 'Done'
