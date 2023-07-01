# Shell Script

*The folder contain about the script to do all thing in system from build, run and deploy into docker*

## Featured
- All in once, everything in system should be used in above file
- Include option from CRUD for target

## Run and use the shell script
1. Need change mode of file into executable if it not already

    `chmod +x <file_you_need_to_change>`

2. Run the shell script by 2 option

    `./<file_you_need_to_run>` or `bash -c <file_you_need_to_run>`


## Options for shell script
1. setup-cadvisor.sh: Do create, delete, start or stop for cadvisor service
    - Create:

        `./setup-cadvisor.sh create <version_you_want_to_set_up>` (Recommended: 0.47.0)

    - Delete:

        `./setup-cadvisor.sh delete`

    - Stop:

        `./setup-cadvisor.sh down`

    - Start:

        `./setup-cadvisor.sh up`

2. setup-node-exporter.sh: Do create, delete, start or stop for node-exporter service (Do Like about cadvisor service but version recommended 1.5.0)

3. setup-swarm-visuallizer.sh: Do create and delete swarm-visuallizer

    - Create

        `./setup-swarm-visuallizer.sh create -n`

    - Delete

        `./setup-swarm-visuallizer.sh destroy`

4. setup-metricserver.sh, setup-monitoring.sh: Do create, delete, start, stop and update

    `./<name_of_file_you_want <create|destroy|up|down|update>` (Not for update into monitoring.sh)

5. setup-swarm.sh: Do create, delete, start and stop

    `./setup-swarm.sh <create|destroy|up|down>` (with create if you have 2 NIC: you need specify the name for create)

6. setup-worker.sh: Do start and stop for worker agent - 2 Mode is supported in V0.2.0

    `./setup-worker.sh <ai|metric> <up|down>`


