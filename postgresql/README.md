# PostgreSQL

PostgreSQL is running as a separate container to the QGIS-nginx-MapProxy cluster to make it clearer that it can be run independently. 

To launch:

    docker-compose up --build

Then use `ogr2ogr` to load geometries into the database. It is running a [postgis](https://hub.docker.com/r/postgis/postgis) image, so PostGIS will be configured but the extension will need to be created in a new database. 