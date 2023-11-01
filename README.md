# qgis_server_tiles
Quickly move from a QGIS map project to a large series of raster map tiles. 

## Directory Structure

- *fonts*: any custom fonts used by your QGIS project. 
- *mapproxy*: configuration files for the MapProxy application.
- *postgresql*: Optional; PostgreSQL data directory. Use this in place of SQLite or other local storage.
- *qgis_data*: Volume-mapped storage for QGIS project and data. 
- *tiles*: Volume-mapped output directory for MapProxy to use for tile storage. 

## Quickstart

1. Create your QGIS project, with all of the data as [relative paths](https://gis.stackexchange.com/questions/20340/saving-project-with-data-source-path-as-relative-in-qgis) to the same directory as the project file. Store data and project files in `./qgis_data`.
2. If your map uses custom fonts, save copies of your required font files in `./fonts` and they will be copied into the QGIS container.
3. Configure your [MapProxy](https://mapproxy.org/) environment by editing the config files in `./mapproxy`. Example files for coverage areas are provided for the US states of Florida, Massachusetts, and New Jersey. Note that New Jersey also covers parts of the New York City metro area.
4. Create the network used by the containers: `docker network create qgis_server_tiles` 
5. Run `docker-compose up -d` to start the containers and detach once running.
6. Start the MapProxy seed process: 

       docker exec -it mapproxy mapproxy-seed \
        -f /mapproxy/mapproxy.yaml \
        -s /mapproxy/seed.yaml -i


## Prerequisites

Software required to be installed:
- Docker

Optional software:
- GDAL/OGR (for GIS data conversion)
- tmux (keep sessions alive and multiplex terminal)
- Python
- AWS command line tools (if working with AWS)

## Optional Processes

### PostgreSQL

The `./postgresql` directory contains a `docker-compose.yml` file that can be used to spin up an instance of PostgreSQL with PostGIS. You can store your data within PostgreSQL, but will need to take additional steps to ensure your connection is properly specified within QGIS. 

### uploadToBucket.py

A Python script to aid in uploading a large amount of files to Amazon S3. As MapProxy defaults to a directory format that is not directly compatible to the TMS/XYZ tile structure, this script will help in creating a SQLite database containing the files to upload and will perform the upload, keeping track of the files previously uploaded to S3. 

Required modules are listed in `requirements.txt`.

For more information: `python3 ./uploadToBucket.py -?` 

## Testing Environment

This was tested on a fresh Debian 12 (bookworm) install running in a VM. The following apt command will help you bootstrap the environment:

    apt install docker gdal-tools gis-devel git spatialite-bin sqlite3

## References 

- QGIS Dockerfile adapted from the [example in QGIS documentation](https://docs.qgis.org/3.28/en/docs/server_manual/containerized_deployment.html).
- QGIS Styling adapted from Anita Graser's [QGIS-resources repo](https://github.com/anitagraser/QGIS-resources/).