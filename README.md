# What is this?

Traefik helper is a tool i developed because of the tedious repetitive task of having to change my config.yaml to put ssl certificates on my websites, so now i only have to input the info of the workloads i want to create and this script makes everything else for me
note: the traefik docker service will not be restarted, you need to restart it yourself manually

# How does it work

First of all it creates files and directories in which the file is gonna work on, then it searches for your traefik.yaml file to locate then the config.yaml file (done like this because you can have more than one config.yaml file on your system), and saves it aswell as some other directories.
After checking everything is correctly setup it starts the program, here you can select between various options

also take note theres always a backup for your services that is called services.json.old which is  the workloads file that was used the last time you opened the script

1. add new service
2. delete an existing service
3. Edit a current service
4. change a workload name
5. check current services
6. save changes
7. save and exit
8. exit without saving

They are most pretty self explanatory but a quick guide here on some:

## 1. add a new service
here you'll be presented with some inputs, you can always change them if you have a typo.
First a workload name is required, it will not be used anywhere in the config.yaml file, is just for this program to work properly and display the info correctly
you will be asked for a name for the name of the service you are providing, this is not critical is more for like identifying the service.
Then the ip will be asked, here you dont need to provide only th eip, you need to enter the current domain of the service (https://192.168.1.80:8080 or http://portainer.xxxx.com if set on pihole for example)
Finally the domain, which will be whatever you want followed with what traefik has set up as domain. I mean, if you have setup traefik as *.local.XXXX.com then you need to enter the following: YYY.local.XXXX.com

## 2. delete a service
You will see the info panel on here, after entering the workload name you want to delete it will no longer show on the info panel, and after saving it will be permanently deleted 

## 3. Edit a current service
This page works same as option 1. the only difference is you can't input a non-existant workload

## 4. change a workload name
If for any reason you want to change a workload name you simply select here and input the workload name you want to change aswell as the new workload ame, all info will be saved

## 5. Check current services
this page is only used to check the currently set up services, them being here doesnt mean they are currently running, is just that they are or will be on the config.yaml file after saving. You need to restart the traefick container for them to start working

## Credits

This script is based on the techotim's traefik 3 blog, what i mean is, he just provided a manual solution which i automatized, also theres an auto-setup tool (that i didn't test yet) that automatically installs it on ubuntu aswell as some other services