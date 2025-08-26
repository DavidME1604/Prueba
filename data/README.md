# Data Sources
## Geoglows
[How to use API Data Service](https://training.geoglows.org/rfs/accessing-data/data-service/)

[Finding River Numbers](https://training.geoglows.org/rfs/accessing-data/find-river-numbers/)

[GEOGLOWS Hydroviewer (Version 1)](https://apps.geoglows.org/apps/geoglows-hydroviewer/)

## CELEC
[CELEC DATA PORTAL](https://generacioncsr.celec.gob.ec/graficasproduccioncelec/index.html)
[CELEC API](https://generacioncsr.celec.gob.ec:8443/ords/csr/sardomcsr/pointValues)

```
curl 'https://generacioncsr.celec.gob.ec:8443/ords/csr/sardomcsr/pointValues?mrid=30031^&fechaInicio=2025-07-29T06:00:00.000Z^&fechaFin=2025-07-30T05:00:00.000Z^&fecha=29/07/2025%2001:00:00' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Origin: https://generacioncsr.celec.gob.ec' \
  -H 'DNT: 1' \
  -H 'Sec-GPC: 1' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://generacioncsr.celec.gob.ec/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'If-None-Match: "8DmIzVpMqalWm0OS2SAD/1VWTe0c99gjrG1xd2w+/dsHXNFuhM4xcvZ32cWYUpmy4FK74aQelh+BgLxHLVIgFw=="' \
  -H 'Priority: u=0'
```
[Slack ref](https://aiskillsaccel-f1l7455.slack.com/archives/C096HS3JK2T/p1753843821611779?thread_ts=1753836849.207499&cid=C096HS3JK2T)
## INAMHI 
[INAMHI GEOGLOWS PORTAL](https://github.com/jusethCS/inamhi-geoglows)

