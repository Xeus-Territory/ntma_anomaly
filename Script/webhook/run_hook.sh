#! /bin/bash

if [ -f .env ]
then
  set -o allexport; source .env; set +o allexport
fi

# echo "python3 scaling_hook -l http://$IP_MANAGER:9090/api/v1/alerts -ti $TI -tm $TM"

bash -c "python3 scaling_hook.py -l http://$IP_MANAGER:9090/api/v1/alerts -ti $TI -tm $TM"