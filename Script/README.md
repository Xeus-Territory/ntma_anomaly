# MANAGE ANYTHING IN FOLDER BY SCRIPT

*following this folder will make easy case to deploy and logical for system NTMA*

## Requirements
- Docker inside the VM or whatever you want to use this repo
- Make sure you have 2 VM or more and make this about became 2 mode manager and worker in docker swarm
- Install apache2-untils, tool for contain API for using to benchmark web application

## Contents of and feature each module:
- [bot](./bot/README.md): The bot command to execute and interact or benchmark webapp --> **Template for request, can be applied for different webapps. By the benchmark just offer for GET requests, others can be developed and tested in next few times.**
- [webhook](./webhook/README.md): Scaling hook where executing the query request from manager and executing the scaling base on flag state
- worker:
    - [bash](./worker/bash/README.md): Shell script to run anything want setup to node Linux
    - [python](./worker/python/README.md): Contain script for automation system and doing specific things for integration