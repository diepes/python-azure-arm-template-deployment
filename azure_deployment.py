#!/usr/bin/env python3

import sys, argparse, logging
import os.path
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
    deployer = Deployer(subscription_id=args.my_subscription_id,
                        resource_group=args.my_resource_group,
                        pub_ssh_key_path=args.my_pub_ssh_key_path,
                        location="australiaeast")

    logging.info("Beginning the deployment... \n\n")
    # Deploy the template

    my_deployment = deployer.deploy()

    logging.warn("Done deploying!!\n\nYou can connect via: `ssh {}@{}.australiaeast.cloudapp.azure.com`".format(args.adminUserName,deployer.dns_label_prefix))
    logging.debug(str(deployer))
    # Destroy the resource group which contains the deployment
    # deployer.destroy()

def main(argv):
    json_template = ''
    parser = argparse.ArgumentParser()
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
                        default='pieter-rg',
                        help="the azure resource group(RG) to deploy the vm in."
                        )
    parser.add_argument("--adminUserName", dest="adminUserName" ,nargs='?',
                        default='pieter',
                        help="the initial ssh user."
                        )

    parser.add_argument("--my_pub_ssh_key_path",
                        default=os.path.expanduser('~/.ssh/id_rsa.pub'),
                        help="initial ssh key rsa public key file for vm login."
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

