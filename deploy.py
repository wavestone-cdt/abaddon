from python_terraform import *
import uuid
import argparse

curr_path=os.path.abspath(os.path.dirname(sys.argv[0]))


parser = argparse.ArgumentParser()
#group = parser.add_mutually_exclusive_group()
parser.add_argument("-a", "--apply", action="store_true", help="Create a new gophish infrastructure")
#group.add_argument("-d", "--destroy", action="store_true")
parser.add_argument('-d','--destroy', nargs='?', help="Destroy a gophish infra (the ec2 uuid has to be given)" )
args = parser.parse_args()


def get_env():
    t = Terraform()
    return [i[2:] for i in t.cmd('workspace list')[1].split('\n') if i.startswith('ec2_',2)]

def create_uuid():
    return 'ec2_'+str(uuid.uuid4())

def print_env():
    print(*get_env(), sep = "\n")

def deploy_ec2(uuid, path):
    print('------------- Creating : ', uuid,' ----------------')
    t = Terraform(working_dir=path)
    if t.create_workspace(uuid)[0] != 0:
        t.set_workspace(uuid)
    t.apply(path, skip_plan=True ,capture_output=False)
    return t.cmd('output -json public_ip | sed s/\"//g')

def destroy_ec2(uuid, path):
    print('------------- Destroying : ', uuid,' ----------------')
    t = Terraform(working_dir=path)
    if t.set_workspace('tree')[0] == 1:
        t.destroy(path ,capture_output=False)
    else:
        print('Unable to destroy instance, workspace does not exsist.')


terraform_path = curr_path + "/terraform/aws"
if args.destroy:
  destroy_ec2(args.destroy, terraform_path)
if args.apply:
  uuid=create_uuid()
  ip = deploy_ec2(uuid, terraform_path)
  with open('/tmp/'+uuid+".txt", 'r') as file:
    password = file.read().replace('\n', '')
  print("Instance created, please connect on port 3333 using admin : "+password+" as credentials")
  print("Once finished, destroy this instance unsing : python3 deploy.py -d "+uuid)
