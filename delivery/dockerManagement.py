import os 
import subprocess
from time import sleep
from .models import Nginx
from django.core.validators import validate_ipv46_address

# Paths to find docker-compose files
LOCAL_PATH_APACHE = "./misc/apache/"
LOCAL_PATH_NGINX = "./misc/nginx/"
LOCAL_PATH_REDELK = "./misc/redelk/"

# Key to use debug error message in a easier way
DOCKER_INSTALL = 'DOCKER_INSTALL'
DOCKER_START = 'DOCKER_START'
DOCKER_COMPOSE_INSTALL = 'DOCKER_COMPOSE_INSTALL'
NGINX_BUILD_AND_RUN = 'NGINX_BUILD_AND_RUN'
APACHE_BUILD_AND_RUN = 'APACHE_BUILD_AND_RUN'
REDELK_BUILD_AND_RUN = 'REDELK_BUILD_AND_RUN'
NGINX_UNDEPLOY = 'NGINX_UNDEPLOY'
APACHE_UNDEPLOY = 'APACHE_UNDEPLOY'
REDELK_UNDEPLOY = 'REDELK_UNDEPLOY'

# Path to the ssh key used on aws instances.
# For now, all aws instances must be accessible with this key
KEY_PATH = './aws/'


# Debug messages
FAILED_MSG = {DOCKER_INSTALL: "[***] Can't install docker on ", \
        DOCKER_START: "[***] Can't start docker on ", \
        DOCKER_COMPOSE_INSTALL: "[***] Can't install docker-compose on ", \
        NGINX_BUILD_AND_RUN: "[***] Can't build or/and run NGINX docker-compose file on ", \
        APACHE_BUILD_AND_RUN: "[***] Can't build or/and run Apache docker-compose file on ", \
        REDELK_BUILD_AND_RUN: "[***] Can't build or/and run RedELK docker-compose file on ", \
        NGINX_UNDEPLOY: "[***] Can't properly undeploy Nginx on ", \
        APACHE_UNDEPLOY: "[***] Can't properly undeploy Apache on ", \
        REDELK_UNDEPLOY: "[***] Can't properly undeploy RedELK on "}

SUCCESS_MSG = {DOCKER_INSTALL: "[*] Docker successfully installed on ", \
        DOCKER_START: "[*] Docker successfully started on ", \
        DOCKER_COMPOSE_INSTALL: "[*] Docker-compose successfully installed on ", \
        NGINX_BUILD_AND_RUN: "[*] NGINX docker container(s) are running on ", \
        APACHE_BUILD_AND_RUN: "[*] Apache docker container(s) are running on ", \
        REDELK_BUILD_AND_RUN: "[*] RedELK docker container(s) are running on ", \
        NGINX_UNDEPLOY: "[*] Nginx successfully undeployed on ", \
        APACHE_UNDEPLOY: "[*] Apache successfully undeployed on ", \
        REDELK_UNDEPLOY: "[*] RedELK successfully undeployed on "}

PENDING_MSG = {DOCKER_INSTALL: "[~] Installing docker on ", \
        DOCKER_START: "[~] Starting Docker on ", \
        DOCKER_COMPOSE_INSTALL: "[~] Installing docker-compose on ", \
        NGINX_BUILD_AND_RUN: "[~] Deploying NGINX docker container on ",\
        APACHE_BUILD_AND_RUN: "[~] Deploying Apache docker container on ", \
        REDELK_BUILD_AND_RUN: "[~] Deploying RedELK docker container on ", \
        NGINX_UNDEPLOY: "[~] Undeploying Nginx on ", \
        APACHE_UNDEPLOY: "[~] Undeploying Apache on ", \
        REDELK_UNDEPLOY: "[~] Undeploying RedELK on "}


def wait_for_success(ec2manager, instance_id, command_exec, action):
    """
        Ensure that the execution of the command was successful.
        Print the associated debug message 
        Return None if the execution has been successful.
               True if the execution has encountered an error
    """
    while True:
        status = ec2manager.get_command_status(command_exec['Command']['CommandId'])
        if status in ['Pending', 'InProgress']:
            print(PENDING_MSG[action] + instance_id[0])
            sleep(1)
            continue
        elif status in ['Failed', 'Cancelled', 'Failed', 'TimedOut', 'Cancelling']:
            print(FAILED_MSG[action] + instance_id[0])
            return True
        else:
            print(SUCCESS_MSG[action] + instance_id[0])
            break


def send_files(path_to_files, path_to_key, user, url):
    """
       Allows to send file to an endpoint through ssh using
       scp.
       Return the return code of the scp command.
    """
    print("[~] Sending files to {}".format(url))
    command_res = subprocess.run(['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-ri', path_to_key, path_to_files, '{}@{}:~'.format(user, url)]) 
    if command_res.returncode:
        print("[***] Error while sending files to {}".format(url))
    else:
        print("[*] File successfully sent to {}".format(url))
    return command_res.returncode


def deploy_nginx(ec2manager, instance_id, instance_ip, target_http_port, target_ssl_port, target_ip):
    """
        Deploy the nginx proxy on the specified ec2 instance
        Return True on succes, False on error
    """
    ### Docker Installation
    try:
        install_docker = ['sudo yum update -y', 'sudo amazon-linux-extras install docker']
        command_exec = ec2manager.run(instance_id, install_docker)
        wait_for_success(ec2manager, instance_id, command_exec, DOCKER_INSTALL)
        ### Start Docker and enable auto start
        start_docker = ['sudo service docker start', 'sudo chkconfig docker on']
        command_exec = ec2manager.run(instance_id, start_docker)
        failed = wait_for_success(ec2manager, instance_id, command_exec, DOCKER_START)
        if failed:
            print("[***] Error : Aborting NGINX container deployment")
            return False
        ### DockerCompose Installation (V 1.22)
        install_docker_compose = ['sudo curl -L \
                https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)\
                -o /usr/local/bin/docker-compose', 'sudo chmod +x /usr/local/bin/docker-compose',\
                'sudo ln -f -s /usr/local/bin/docker-compose /usr/bin/docker-compose']
        command_exec = ec2manager.run(instance_id, install_docker_compose)
        failed = wait_for_success(ec2manager, instance_id, command_exec, DOCKER_COMPOSE_INSTALL)
        if failed:
            print("[***] Error : Aborting NGINX container deployment")
            return False
        ### Sending files to EC2 instance :
        
        if send_files('misc/nginx/', KEY_PATH + ec2manager.get_key_pair_name(instance_id) + '.pem', 'ec2-user', instance_ip):
            print("[***] Error : Aborting NGINX container deployment")
            return False
        ### Deploy docker
        ### It's important to use the --no-cache parameter in order to avoid problem
        ### Especially when you want to undeploy and redeploy with other options
        build_docker = 'sudo docker-compose -f /home/ec2-user/nginx/docker-compose.yml build \
                --build-arg IP_target={} \
                --build-arg httpPort={} \
                --build-arg sslPort={} --no-cache'.format(target_ip, target_http_port, target_ssl_port)
        print(build_docker)
        run_docker = 'sudo docker-compose -f /home/ec2-user/nginx/docker-compose.yml up -d'
        command_exec = ec2manager.run(instance_id, [build_docker, run_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, NGINX_BUILD_AND_RUN)
        if failed:
            print("[***] Error : Aborting NGINX container deployment")
            return False
    except:
        print("[***] Error : Aborting NGINX container deployment")
        return False

    return True

def deploy_redelk(trusted_ip, instance_ip, on_aws, http_port=None, ssl_port=None, ec2manager=None, instance_id=None, listener_port=None, C2_ip=None):
    """
        Call the deployment process of redelk regarding the on_aws parameter.
        Return True on success, False on error
    """
    if on_aws:
        return deploy_redelk_on_aws(ec2manager, instance_ip, [instance_id], trusted_ip, http_port, ssl_port, listner_port, C2_IP)
    return deploy_redelk_local(trusted_ip, http_port, ssl_port, listener_port, C2_ip)

def deploy_redelk_local(trusted_ip, http_port, ssl_port, listener_port, C2_ip):
    """
        Deploy the redelk infrastructure localy
        Return The kibana local ip on success, False on error
    """
    # The elk version still needs to be updated manually.
    elk_version = "7.0.1"
    # Ensure that docker is available on the local host
    verify_docker = subprocess.run(["docker", "-v"])
    if not verify_docker.returncode:
        print("[*] Docker Ready")
    else:
        print("[***] Docker not ready : need to check requirements and follow the install process")
        return False
    # Ensure that docker_compose is available on the local host
    verify_docker_compose = subprocess.run(["docker-compose", "-v"])
    if not verify_docker_compose.returncode:
        print("[*] DockerCompose Ready")
    else:
        print("[***] DockerCompose not ready : \
                need to check requirements and follow the install process")
        return False
    # Deploy Redelk containers
    build_redelk_cmd = subprocess.run(["ELK_VERSION={} \
                                        docker-compose \
                                        -f \
                                        {} \
                                        build".format(elk_version, LOCAL_PATH_REDELK + "docker-compose.yml")], \
                                        shell=True)
    deploy_redelk_cmd = subprocess.run(["ELK_VERSION={} \
                                        docker-compose \
                                        -f \
                                        {} \
                                        up -d".format(elk_version, LOCAL_PATH_REDELK + "docker-compose.yml")], \
                                        shell=True)
    if not (deploy_redelk_cmd.returncode or build_redelk_cmd.returncode):
        print("[*] RedELK successfully deployed")
    else:
        print("[***] RedELK deployment failed")
        return False
    # Deploy Apache (and filebeats) containers
    # As we have to use os.system and we have to be sure that the arguments we are passing are
    # trustabe. This is why we validate manually that all the data passed by the user can be
    # interpreted as the expected type.
    try:
        validate_ipv46_address(trusted_ip)
        http_port = int(http_port)
        ssl_port = int(ssl_port)
        listener_port = int(listener_port)
        validate_ipv46_address(C2_ip)
    except:
        print("[***] Error in http_port, ssl_port, or trustedIp")
        return False

    # Here using a subprocess function with the argument Shell=True shouldn't be
    # a problem anymore as we are sure that we are mastering all the parameters
    build_apache = subprocess.run(['http_port={} \
                                    ssl_port={} \
                                    docker-compose -f {} \
                                        build --build-arg ELK_VERSION="{}" \
                                              --build-arg TrustedIP="{}" \
                                              --build-arg ListenerPort="{}" \
                                              --build-arg C2_IP="{}" \
                                              '.format(http_port,
                                                       ssl_port,
                                                       LOCAL_PATH_APACHE + "docker-compose.yml",
                                                       elk_version,
                                                       trusted_ip,
                                                       listener_port,
                                                       C2_ip)], shell=True)
    deploy_apache = subprocess.run(['http_port={} ssl_port={} \
                                    docker-compose \
                                    -f {} up -d'.format(http_port, \
                                                        ssl_port, \
                                                        LOCAL_PATH_APACHE + "docker-compose.yml")], \
                                    shell=True)

    if not (deploy_apache.returncode or build_apache.returncode):
        print("[*] Apache server successfully deployed")
    else:
        print("[***] Apache deployment failed")
        return False
    # Get the ip adress of the kibana docker instance
    kibana_access = subprocess.check_output(["docker ps -q | xargs -n 1 docker inspect --format '{{ .NetworkSettings.Networks.elk.IPAddress }} {{ .Name }}' | sed 's/ \// /' | grep redelk_nginx | cut -d ' ' -f1"], shell=True)
    kibana_access = kibana_access[:-1]
    print("RedELK is ready to be used")
    return kibana_access.decode("utf-8")


def deploy_redelk_on_aws(ec2manager, instance_ip, instance_id, trusted_ip, http_port, ssl_port, listener_port, C2_ip):
    """
        Deploy redelk infrastructure on aws (used for debug and test purpose only)
        Return True on sucess, False on Error
    """
    try:
        ### Docker Installation
        install_docker = ['sudo apt-get update',
                          'sudo apt-get install apt-transport-https ca-certificates curl \
                                  gnupg-agent software-properties-common',
                          'curl -fsSL https://download.docker.com/linux/ubuntu/gpg |\
                                  sudo apt-key add -',
                          'sudo add-apt-repository \
                                  "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
                                  $(lsb_release -cs) stable"',
                          'sudo apt-get update',
                          'sudo apt-get install -y docker-ce docker-ce-cli containerd.io']
        command_exec = ec2manager.run(instance_id, install_docker)
        failed = wait_for_success(ec2manager, instance_id, command_exec, DOCKER_INSTALL)
        if failed:
            print("[***] Error : Aborting deploying APACHE/REDELK containers")
            return False
        ### DockerCompose Installation (V 1.22)
        install_docker_compose = ['sudo curl -L \
                https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)\
                -o /usr/local/bin/docker-compose', 'sudo chmod +x /usr/local/bin/docker-compose']
        command_exec = ec2manager.run(instance_id, install_docker_compose)
        failed = wait_for_success(ec2manager, instance_id, command_exec, DOCKER_COMPOSE_INSTALL)
        if failed:
            print("[***] Error : Aborting deploying APACHE/REDELK containers")
            return False
        ### Sending files to EC2 instance :
        if send_files('misc/apache/', KEY_PATH + ec2manager.get_key_pair_name(instance_id) + '.pem', 'ubuntu', instance_ip) or \
                send_files('misc/redelk/', KEY_PATH + ec2manager.get_key_pair_name(instance_id) + '.pem', 'ubuntu', instance_ip):
            print("[***] Error : Aborting deploying NGINX container")
            return False
        ### Find a way to retrieve the elk version
        elk_version = "7.0.1"
        ### RedELK docker
        build_docker = 'sudo ELK_VERSION="{}" docker-compose \
                -f /home/ubuntu/redelk/docker-compose.yml build'.format(elk_version)
        run_docker = 'sudo ELK_VERSION="{}" docker-compose \
                -f /home/ubuntu/redelk/docker-compose.yml up -d'.format(elk_version)
        command_exec = ec2manager.run(instance_id, [build_docker, run_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, REDELK_BUILD_AND_RUN)
        if failed:
            print("[***] Error : Aborting deploying APACHE/REDELK containers")
            return False
        ### Apache docker
        build_docker = 'sudo http_port={} ssl_port={} \
                docker-compose -f /home/ubuntu/apache/docker-compose.yml build \
                --build-arg ELK_VERSION="{}" \
                --build-arg TrustedIP="{}" \
                --build-arg ListenerPort={} \
                --build-arg C2_IP={}'.format(http_port, ssl_port, elk_version, trusted_ip, listener_port, C2_ip)
        run_docker = 'sudo http_port={} ssl_port={} \
                docker-compose -f /home/ubuntu/apache/docker-compose.yml up -d'.format(http_port, ssl_port)
        command_exec = ec2manager.run(instance_id, [build_docker, run_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, APACHE_BUILD_AND_RUN)
        if failed:
            print("[***] Error : Aborting deploying APACHE/REDELK containers")
            return False
    except:
        print("[***] Error : Aborting deploying APACHE/REDELK containers")
        return False

    return True


def undeploy_nginx(ec2manager, nginx_aws):
    """
        Undeploy nginx previously deployed on an aws instance
    """
    try:
        stop_docker = 'sudo docker-compose -f /home/ec2-user/nginx/docker-compose.yml down'
        instance_id = [nginx_aws.aws_id]
        command_exec = ec2manager.run(instance_id, [stop_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, NGINX_UNDEPLOY)
    except:
        failed = True

    if failed:
        print("[***] Error : Aborting undeploying NGINX containers")
        return False

    try:
        nginx_aws.nginx_aws_instance.delete()
    except:
        pass

    return True

def undeploy_redelk(redelk, on_aws, ec2manager=None):
    """
        Undeploy redelk previously deployed on aws or locally regarding
        the value of the on_aws parameter
        Return True on success, False on error
    """
    if on_aws:
        return undeploy_redelk_aws(ec2manager, redelk)
    return undeploy_redelk_local(redelk)


def undeploy_redelk_aws(ec2manager, redelk_aws):
    """
        Undeploy redelk previously deployed on aws.
        Return True on success, False on Error
    """
    try:
        instance_id = [redelk_aws.aws_id]
        stop_docker = 'sudo http_port=0 ssl_port=0 docker-compose -f /home/ubuntu/apache/docker-compose.yml down'
        command_exec = ec2manager.run(instance_id, [stop_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, APACHE_UNDEPLOY)
        if failed:
            print("[***] Error : Aborting undeployment of Apache and RedELK")
            return False
        stop_docker = 'sudo docker-compose -f /home/ubuntu/redelk/docker-compose.yml down'
        ec2manager.run(instance_id, [stop_docker])
        failed = wait_for_success(ec2manager, instance_id, command_exec, REDELK_UNDEPLOY)
        if failed:
            print("[***] Error : Aborting undeployment of Apache and RedELK")
            return False
    except:
        print("[***] Error : Aborting undeployment of Apache and RedELK")
        return False

    try:
        redelk_aws.redelk_aws_instance.delete()
    except:
        pass

    return True


def undeploy_redelk_local(redelk_local):
    """
        Undeploy redelk previously deployed locally
        Return True on success, False on error
    """
    # It's mandatory to set http_port and ssl_port (even with arbitrary value
    # Otherwise the down command fail because docker-compose consider that the configuration file
    # is invalid
    try:
        apache_undeploy = subprocess.run(["http_port=0 \
                                           ssl_port=1  \
                                           docker-compose  \
                                           -f  \
                                           {} \
                                           down".format(LOCAL_PATH_APACHE+"docker-compose.yml")], \
                                           shell=True)
        if apache_undeploy.returncode:
            print("[***] Error : Aborting undeployment Apache and RedELK")
            return False
        redelk_undeploy = subprocess.run(["docker-compose", \
                                          "-f", \
                                          LOCAL_PATH_REDELK + "docker-compose.yml",
                                          "down"])
        if redelk_undeploy.returncode:
            print("[***] Error : Aborting undeployment Apache and RedELK")
            return False
    except:
        print("[***] Error : Aborting undeployment Apache and RedELK")
        return False

    try:
        redelk_local.redelk_local_instance.delete()
    except:
        pass

    return True
