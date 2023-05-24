> **NOTE**
>
> Run: `docker compose -f get-data-metric-compose.yaml up -d`
>
> wait a few seconds after the kafka service is up
>
> Run: `docker exec -it redis redis-cli`
>
> Command: `KEYS *` => Review.