---
services: azure-resource-manager
platforms: python
author: pieter.e.smit
original: nothing to commit, working tree clean
---

# Deploy an SSH Enabled VM with a Template in Python

This sample explains how to use Azure Resource Manager templates to deploy your Resources to Azure. 
It shows how to deploy your Resources by using the Azure SDK for Python.

When deploying an application definition with a template, you can provide parameter values to customize how the
resources are created. You specify values for these parameters either inline or in a parameter file.

## Incremental and complete deployments

By default, Resource Manager handles deployments as incremental updates to the resource group. With incremental
deployment, Resource Manager:

- leaves unchanged resources that exist in the resource group but are not specified in the template
- adds resources that are specified in the template but do not exist in the resource group
- does not re-provision resources that exist in the resource group in the same condition defined in the template

With complete deployment, Resource Manager:

- deletes resources that exist in the resource group but are not specified in the template
- adds resources that are specified in the template but do not exist in the resource group
- does not re-provision resources that exist in the resource group in the same condition defined in the template

You specify the type of deployment through the Mode property, as shown in the examples below.

## Deploy with Python

In this sample, we are going to deploy a resource template which contains an Ubuntu LTS virtual machine using
ssh public key authentication, storage account, and virtual network with public IP address. The virtual network
contains a single subnet with a single network security group rule which allows traffic on port 22 for ssh with a single
network interface belonging to the subnet. The virtual machine is a `Standard_D1` size. You can find the template [here](/templates)

### To run this sample, do the following:

1. If you don't already have it, [install Python](https://www.python.org/downloads/).

1. We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to run this example,
    but it's not mandatory.
    To initialize a virtual environment:

    ```
    pip install virtualenv
    virtualenv venv
    cd venv
    source bin/activate
    ```

1. Create a Service Principal
    [Azure CLI](https://azure.microsoft.com/documentation/articles/resource-group-authenticate-service-principal-cli/),
   
1. Clone this repository and navigate into it.

    ```
    git clone https://github.com/Azure-Samples/resource-manager-python-template-deployment.git
    cd resource-manager-python-template-deployment
    ```
1. Install all required libraries within the virtual environment.

   ```
   pip install -r requirements.txt
   ```

1. Create environment variables with the necessary IDs for Azure authentication.
    If you login using the Azure az cli, the credentials will be saved locally and used by the script.

    You can learn where to find the first three IDs in the Azure portal in [this document](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal#get-application-id-and-authentication-key).
 
    Manual settings if not using az credentials.
    The subscription ID is in the subscription's overview in the "Subscriptions" blade of the portal.
    ```
    export AZURE_TENANT_ID={your tenant id}
    export AZURE_CLIENT_ID={your client id}
    export AZURE_CLIENT_SECRET={your client secret}
    export AZURE_SUBSCRIPTION_ID={your subscription id}
    ```

1. Run the script.
    
    ```
    python azure_deployment.py
    ```

### What is this azure_deployment.py Doing?

The entry point for this sample is [azure_deployment.py](https://github.com/azure-samples/resource-manager-python-template-deployment/blob/master/azure_deployment.py). This script uses the `Deployer` class
below to deploy the aforementioned template to the subscription and resource group specified in `my_resource_group`
and `my_subscription_id` respectively. By default the script will use the ssh public key from your default ssh
location.
By default is also runs the `templates/bootstrap-nsp-script.sh` on the newly created server. (Installs salt)



### What is this deployer.py Doing?

The [Deployer class](https://github.com/azure-samples/resource-manager-python-template-deployment/blob/master/lib/deployer.py) consists of the following:

The `__init__` method initializes the class with the subscription, resource group and public key. The method also fetches
the Azure Active Directory bearer token, which will be used in each HTTP request to the Azure Management API. The class
will raise exceptions under two conditions: if the public key path does not exist, or if there are empty
values for `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` or `AZURE_CLIENT_SECRET` environment variables.

The `deploy` method does the heavy lifting of creating or updating the resource group, preparing the template
parameters and deploying the template.

The `destroy` method simply deletes the resource group thus deleting all of the resources within that group.
Note that it is commented out in `azure_deployment.py`. But you can uncomment it to easily clean up the resources
created by this sample if you no longer need them.

Each of the above methods use the `azure.mgmt.resource.ResourceManagementClient` class, which resides within the
[azure-mgmt-resource](https://pypi.python.org/pypi/azure-mgmt-resource/) package ([see the docs here](http://azure-sdk-for-python.readthedocs.io/en/latest/resourcemanagement.html)).

After the script runs, you should see something like the following in your output:

```
$ python azure_deployment.py

Initializing the Deployer class with subscription id: 11111111-1111-1111-1111-111111111111, resource group: azure-python-deployment-sample
and public key located at: /Users/you/.ssh/id_rsa.pub...

Beginning the deployment...

Done deploying!!

You can connect via: `ssh azureSample@damp-dew-79.westus.cloudapp.azure.com`
```

You should be able to run `ssh azureSample@{your dns value}.{location}.cloudapp.azure.com` to connect to your new VM.
