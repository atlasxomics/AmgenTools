# PortableAtlasTools

### AWS ec2 configurations:
Note: We created our own AMI with these settings below

- Instance type: t2.xlarge
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

config.yml file is required to be ready with AWS credentials as well as bucket-name. config_template.yml can be copied and furnished with required parameters.
The config file must be placed inside the folder PortablAtlaseTool and in PortableAtlasTools/workers

### s3 bucket structure
Below will be the necessary naming scheme for the folders within the s3

- <company_name>-atx-cloud
  - This will contain data to be analyzed in AtlasXplore
- <company_name>-atx-illumina
  - This will contain data to be processed in AtlasXBrowser
 
### Commands to start docker containers
```
docker network create atx-cloud
cd /root/AmgenTools/dockerfiles
docker-compose up -d
```

### Commands to clean up all docker systems
```
cd /root/PortableAtlasTools/dockerfiles
docker-compose down
docker system prune -a 
```
After the last command. Enter y when prompted and then click Enter/Return

### How to manually change bucket name

In PortableAtlasTools there will be a python script to update the necessary files. Make sure both configs are updated to match the tempalte.
The command to run it is below and format of input will be **old_bucket,new_bucket**
```
python update_bucket.py
```

