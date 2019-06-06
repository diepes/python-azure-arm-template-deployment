#!/usr/bin/env python3

import sys, argparse, logging
import os.path
print("Not used anymore - integrated into deployment 2018-11-05")
print("  9s-saltstack-config/azure-9s-arm-deploy")
sys.exit(1)
# logging level set with -v flag
logging.basicConfig(level=logging.WARNING,format='[%(levelname)-5s] %(message)s')
logging.warning("Start!")


def run(args):
    ''' main script  after arguments '''
    from deployer import Deployer

    # This script expects that the following environment vars are set:
    #
    # AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
    # AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
    # AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret


    msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {}" \
          "\nand public key located at: {}...\n\n"
    msg = msg.format(args.my_subscription_id, args.my_resource_group, args.my_pub_ssh_key_path)
    logging.info(msg)

    # Initialize the deployer class
    deploy = Deployer(subscription_id=args.my_subscription_id,
                        location=args.location
                        )
    ##

    logging.info("Beginning the deployment... \n\n")
    # Deploy the template
    args.dns_label_prefix = args.vmName.lower()    ##re ^[a-z][a-z0-9-]{1,61}[a-z0-9]$

    deploy.deploy( vars(args) )

    logging.warn("Done deploying!!\n\nYou can connect via: `ssh {}@{}.australiaeast.cloudapp.azure.com`".format(args.adminUserName,args.dns_label_prefix))
    logging.debug(str(deploy))
    # Destroy the resource group which contains the deployment
    # deployer.destroy()

def main(argv):
    example_text = '''example:

 # time ./azure_deployment.py --resource_group DEV01 --vmName ALL01DEV01AEA01 --rgVNET VNET-NONPRD --virtualNetworkName VNET-NONPRD
                   '''

    parser = argparse.ArgumentParser(epilog=example_text,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", action="count",
                        default=0,
                        help="increase output verbosity"
                        )
    parser.add_argument(dest="template", nargs='?', type=str,
                        default="templates/template.json",
                        help="template to deploy on azure."
                        )
    parser.add_argument("--subscription_id",dest="my_subscription_id",nargs='?', type=str,
                        default=os.environ.get('AZURE_SUBSCRIPTION_ID', ''),
                        help="azure subscription_id , default picked from environment AZURE_SUBSCRIPTION_ID"
                        )
    parser.add_argument("--resource_group", dest="my_resource_group" ,nargs='?',
                        help="the azure resource group(RG) to deploy the vm in. e.g. DEV01"
                        )
    parser.add_argument("--adminUserName", nargs='?',
                        default='admin9sp',
                        help="the initial ssh user."
                        )
    parser.add_argument("--location", nargs='?',
                        default='australiaeast',
                        help="azure datacenter location."
                        )
    parser.add_argument("--vmSize", nargs='?'
                        ,default='Standard_E4s_v3'
                        ,help="azure vm size to use. 'Standard_D2s_v3'-2cpu-8gig-$136 , 'Standard_E2s_v3'-2cpu-16gig-$174, 'Standard_E4s_v3'-4cpu-32gig-$344 "
                        )
    parser.add_argument("--vmName", nargs='?'
                        ,help="the minion ID.upper() 15char, and azure VM resource name."
                        , type=lambda s: s[0:14]+s[14]
                        )
    parser.add_argument("--rgVNET" ,nargs='?',
                        help="the azure resourceGroup VNET to use."
                        )
    parser.add_argument("--virtualNetworkName" ,nargs='?',
                        help="the azure resourceGroup VNET to use."
                        )

    parser.add_argument("--my_pub_ssh_key_path",
                        #default=os.path.expanduser('~/.ssh/id_rsa.pub'),
                        default=os.path.expanduser('~/.ssh/authorized_keys'),
                        help="initial ssh key rsa public key file for vm login. Others in bootstrap."
                        )
    parser.add_argument("--bootstrapfile",
                        default=('templates/bootstrap-nsp-script.sh'),
                        help="bootstrap salt install."
                        )
    parser.add_argument("--salt_map",nargs='?',
                        help=' salt template look in /etc/salt/cloud.maps.d/*/*.conf',
                        )
    parser.add_argument("--imageSku" , nargs='?',
                        default=('16.04-LTS'),
                        help="Linux image to load e.g. '14.04.5-LTS'  ,  '16.04-LTS'  "
                        )
    args = parser.parse_args()

    if args.verbose > 0:
        log=logging.getLogger()
        log.setLevel(logging.INFO)
        logging.info(f"set logging.level to INFO verbose={args.verbose}")
    if args.verbose > 1:
        log.setLevel(logging.DEBUG)
        logging.debug(f"set logging.level to DEBUG verbose={args.verbose}")

    logging.debug(f"{argv[0]} args is {args}")

    run(args) #args also parsed to azure template.json

if __name__ == "__main__":
    main(sys.argv)

