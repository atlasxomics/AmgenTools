# AmgenTools

### AWS ec2 configurations:
Note: We created our own AMI with these settings below

- Instance type: t2.large
- vCPU: 4
- Platform: Ubuntu
- Platform details: Linux/UNIX

### Necessary technologies
These need to be installed on the ec2 instance
- docker
  - Follow the instruction in this section [Install using the apt repository](https://docs.docker.com/engine/install/ubuntu/)
- docker-compose
  - Follow instructions for [Step 1](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)
 
### Config File details

config.yml file is required to be ready with AWS credentials as well as other options. config_template.yml can be copied and furnished with required parameters. When creating s3 bucket folder structure it will need to match what is defined in the config.yml file

### s3 bucket structure
Below will be the necessary naming scheme for the folders within the s3

- atx-track-host
  - In this folder upload the folder in the git repo named [ref]()
