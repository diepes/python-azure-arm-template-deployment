"""A deployer class to deploy a template on Azure"""
import os.path
import json
import yaml
#from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
#PES
from azure.common.client_factory import get_client_from_cli_profile
import base64
import subprocess

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """



    def __init__(self, subscription_id, resource_group, location ):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location

        def get_resource_client():
            from azure.mgmt.resource import ResourceManagementClient
            return get_client_from_cli_profile(ResourceManagementClient)

        try:
            self.credentials = ServicePrincipalCredentials(
                client_id=os.environ['AZURE_CLIENT_ID'],
                secret=os.environ['AZURE_CLIENT_SECRET'],
                tenant=os.environ['AZURE_TENANT_ID']
            )
            self.client = ResourceManagementClient(self.credentials, self.subscription_id)
        except KeyError:
            self.client = get_resource_client()
        except Exception as inst:
            print("type:",type(inst))    # the exception instance
            print("args:",inst.args)     # arguments stored in .args
            print("inst:",inst)
            raise

    def deploy(self,args={}):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location': self.location
            }
        )

        # Will raise if file not exists or not enough permission
        pub_ssh_key = ""
        for pub_ssh_key_path in [ args['my_pub_ssh_key_path'] ]:
            pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
            with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
                pub_ssh_key = pub_ssh_key +  pub_ssh_file_fd.read()
        pub_ssh_key = pub_ssh_key.strip()
        print("ssh keys:  ",pub_ssh_key)


        #Generate bootstrap file with minion config
        with open(os.path.abspath(args['bootstrapfile']), 'r') as b_boot:
            script = b_boot.read()

        #Read minion config from /etc/salt/cloud......
        with open(os.path.abspath(args['salt_map']), 'r') as b_salt:
            salt_map = yaml.load(b_salt)
            print("salt:",salt_map)
            found_config_match = False
            for salt_profile,v in salt_map.items():  ## CPU5_RAM8 : [{ ALL02 ...
                for salt_vms in v:  #loop through list [ { vm1 : {...}}, { vm2 : {...}}, ]
                    for salt_vm_id,salt_conf in salt_vms.items():
                        print("salt_vm_id:",salt_vm_id)
                        print("salt_conf:",salt_conf)
                        if salt_vm_id == args['vmName']:
                            print(f"INFO vmName:{args['vmName']} found in map.")
                            salt_id=args['vmName'].upper()
                            salt_conf['minion']['id']=salt_id
                            salt_minion = salt_conf['minion']
                            salt_grains = salt_conf['grains']
                            print(f"from salt map import keys: {salt_conf['azure']}")
                            args.update( salt_conf['azure'] ) ##Load azure settings from salt pillar.
                            found_config_match = True
                            break
                        else:
                            print(f"Warning vmName:{args['vmName']} != salt_map:{salt_vm_id}")
                            continue
                    if found_config_match: break
                if found_config_match: break
            if not found_config_match:
                 print(f" did not find {args['vmName']} in the {args['salt_map']} map file.")
                 exit(1)
            #print(f"minion: \n{ yaml.dump(salt_minion,default_flow_style=False) }\ngrains: \n{yaml.dump(salt_grains, default_flow_style=False)}")
            #
        #Generate a minion pre-seed key for use with salt master.
        subprocess.run(f"sudo salt-key --gen-keys={salt_id} --gen-keys-dir=/tmp", shell=True)
        subprocess.run(f"sudo cp /tmp/{salt_id}.pub /etc/salt/pki/master/minions/{salt_id}", shell=True)
        with open(os.path.abspath(f'/tmp/{salt_id}.pem'), 'r') as f_salt_key:
            salt_key_pem = f_salt_key.read()
        with open(os.path.abspath(f'/tmp/{salt_id}.pub'), 'r') as f_salt_key:
            salt_key_pub = f_salt_key.read()
        subprocess.run(f"sudo rm /tmp/{salt_id}.pub", shell=True)
        subprocess.run(f"sudo rm /tmp/{salt_id}.pem", shell=True)

        # 1st encode() string(utf8) to binary, and final decode() is b'' back to string.
        script = script.format(salt_minion=yaml.dump(salt_minion,default_flow_style=False)
                              ,salt_grains=yaml.dump(salt_grains, default_flow_style=False)
                              ,salt_key_pem=salt_key_pem
                              ,salt_key_pub=salt_key_pub
                              )
        print();print(script);print()
        #base64 encode bootstrap and add to azure arm template.
        bootstrapScriptBase64 = base64.b64encode( script.encode() ).decode()
        print(len(bootstrapScriptBase64))

        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'template.json')
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)
        print(template['parameters'].keys())
        print()
        print(args.keys())
        parameters = {
            'sshKeyData': pub_ssh_key,
            'dnsLabelPrefix':  args['dns_label_prefix'],
            'bootstrapScriptBase64' : bootstrapScriptBase64,
            'vmEnvironment': self.resource_group,

        }
        #Add all matching args values to parameters.
        for k,v in args.items():
            if k in template['parameters']:
                print("match args key=",k,":",v)
                parameters[k]=v
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }
        #exit(0)
        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'azure-sample',
            deployment_properties
        )
        deployment_async_operation.wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group)
