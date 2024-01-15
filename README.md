# big-map-archive-api-client

> This is a command line client to interact with BIG-MAP Archive data repositories.
> Use version 1.1.0 to connect to the BIG-MAP Archive version with invenioRDM v9.
> Use version 1.1.2 to connect to the BIG-MAP Archive version with invenioRDM v12.

## Table of contents

- [Quick start](#quick-start)
  - [Installation](#installation)
  - [Configuration files](#configuration-files)
  - [Metadata files](#metadata-files)
  - [Data files](#data-files)
- [Usage](#usage)
  - [Overview](#overview)
  - [Get records](#get-records)
  - [Create records](#create-records)
  - [Update records](#update-records)
  - [Back up FINALES databases](#back-up-finales-databases)
- [Back-up policy for FINALES databases](#back-up-policy-for-finales-databases)
  
## Quick start

### Installation

`big-map-archive-api-client` is a Python package hosted on [PyPI](https://pypi.org/project/big-map-archive-api-client/).

We recommend that you proceed as follows to install the Python package and its dependencies on a Linux machine:

1. Create a virtual environment

```bash
python -m venv /home/<username>/.virtualenvs/<virtual_env_name>
```

2. Activate the virtual environment

```bash
source /home/<username>/.virtualenvs/<virtual_env_name>/bin/activate
```

3. Install the `wheel` package if needed (see [here](https://stackoverflow.com/questions/69369669/python-3-venv-and-the-wheel-package))

```bash
pip install wheel
```

4. Install the `big-map-archive-api-client` package along with its dependencies in the virtual environment:
Use version 1.1.0 to connect to the BIG-MAP Archive version with invenioRDM v9.
Use version 1.1.2 to connect to the BIG-MAP Archive version with invenioRDM v12.

```bash
pip install big-map-archive-api-client==1.1.0
pip install big-map-archive-api-client==1.2.0
```

5. [Optional] Once installed, check that the executable file associated with `bma` is indeed located in the virtual environment:

```bash
which bma
```

6. [Optional] Create a project directory (to store configuration, input, and output files).

### Configuration files

Each command requires a YAML configuration file that specifies the domain name and an API token for the targeted data repository. 
This is indicated by the command options `--config-file` and `--bma-config-file`. 
We also recommend to place such a file in your project directory and to name it `bma_config.yaml`. Its content should be similar to:

```yaml
domain_name: "big-map-archive-demo.materialscloud.org" # Options: archive.big-map.eu, big-map-archive-demo.materialscloud.org, big-map-archive-demo-public.materialscloud.org
token: "123456789"
```

Note that to get an API token for the targeted BIG-MAP Archive, you need an account on the data repository. 
To request an account, email us at big-map-archive@materialscloud.org. 
Once logged in, navigate to `https://<archive_domain_name>/account/settings/applications` and create a token.

The command `bma finales-db back-up` requires another YAML configuration file that specifies the IP address and the port for the targeted FINALES server, and credentials for a user account on the server.
This corresponds to the command option `--finales-config-file`. 
We recommend to place such a file in your project directory and to name it `finales_config.yaml`. Its content should be similar to:
```yaml
ip_address: "0.0.0.0" # Replace by IP address for a FINALES server
port: "1234" # Replace by port for a FINALES server
username: "test" # Replace by valid username
password: "test" # Replace by valid password
```

### Metadata files

Several commands (e.g., `bma record create`) use a YAML file specified by the command option `--metadata-file` to create/update a record's metadata. 
We recommend to place such a file in your project directory and to name it `metadata.yaml`. Its content should be similar to:

```yaml
resource_type: "Dataset" # Choose one of these options: Dataset, Software, Other
title: "Mobilities in Two-Dimensional Materials" # Record's title
authors: # Record's list of authors with their affiliations
  - family_name: "Doe"
    given_name: "Jane"
    affiliations:
      - "Physics Institute, École Polytechnique Fédérale de Lausanne, CH-1015 Lausanne, Switzerland"
  - family_name: "Dell"
    given_name: "John"
    affiliations:
      - "Department of Physics, Technical University of Denmark (DTU), 2800 Kongens Lyngby, Denmark"
      - "Physics Institute, École Polytechnique Fédérale de Lausanne, CH-1015 Lausanne, Switzerland"
description: "Two-dimensional materials are emerging as a promising platform for ultrathin channels..." # Abstract-like description of the record
license: "BIG-MAP Archive License" # Choose one of these options: BIG-MAP Archive License, Creative Commons Attribution Share Alike 4.0 International, MIT License
keywords: # Any keyword is accepted
  - "2D materials"
  - "transport"
references: # Choose among these options for the reference scheme: arxiv, doi, isbn, url
  - scheme: "arxiv"
    identifier: "2308.08462"
  - scheme: "doi"
    identifier: "10.1093/ajae/aaq063"
  - scheme: "isbn"
    identifier: "978-3-16-148410-0"
  - scheme: "url"
    identifier: "https://arxiv.org/abs/2308.08462"
```

### Data files

Two commands offer the possibility to attach data files of your choosing to your records: `bma record create` and `bma record update`.

Please comply with the following rules: 
- a maximum of 100 files per record and 
- a total file size smaller than 100 GB per record.

The command option `--data-files` should point to the directory where the files to be uploaded and attached to the new record are located. We usually place such a folder in our project directory and name it `upload`.

## Usage

You may want to test a command against a [demo instance](https://big-map-archive-demo.materialscloud.org/), before executing it against the [main data repository](https://archive.big-map.eu/).

### Overview

```
bma --help
```
```text
Usage: bma [OPTIONS] COMMAND [ARGS]...

  Command line client to interact with a BIG-MAP Archive.

Options:
  --help  Show this message and exit.

Commands:
  finales-db  Copy data from the database of a FINALES server to a...
  record      Manage records on a BIG-MAP Archive.
```

```bash
bma record --help
```

```text
Usage: bma record [OPTIONS] COMMAND [ARGS]...

  Manage records on a BIG-MAP Archive.

Options:
  --help  Show this message and exit.

Commands:
  create   Create a record on a BIG-MAP Archive and optionally publish it.
  get      Get the metadata of a published version of an entry on a...
  get-all  Get the metadata of the latest published version for each...
  update   Update a published version of an archive entry, or create a...
```

```bash
bma finales-db --help
```

```text
Usage: bma finales-db [OPTIONS] COMMAND [ARGS]...

  Copy data from the database of a FINALES server to a BIG-MAP Archive.

Options:
  --help  Show this message and exit.

Commands:
  back-up  Perform a partial back-up from the database of a FINALES...
```

### Get records

```bash
bma record get --help
```

```text
Usage: bma record get [OPTIONS]

  Get the metadata of a published version of an entry on a BIG-MAP Archive and
  save it to a file.

Options:
  --config-file FILE  Path to the YAML file that specifies the domain name and
                      a personal access token for the targeted BIG-MAP
                      Archive. See bma_config.yaml in the GitHub repository.
                      [required]
  --record-id TEXT    Id of the published version of an archive entry (e.g.,
                      "pxrf9-zfh45").  [required]
  --output-file FILE  Path to the JSON file where the obtained record's
                      metadata will be exported to.  [required]
  --help              Show this message and exit.
```

```bash
bma record get-all --help
```

```text
Usage: bma record get-all [OPTIONS]

  Get the metadata of the latest published version for each entry on a BIG-MAP
  Archive and save them to a file.

Options:
  --config-file FILE  Path to the YAML file that specifies the domain name and
                      a personal access token for the targeted BIG-MAP
                      Archive. See bma_config.yaml in the GitHub repository.
                      [required]
  --all-versions      Get all published versions for each entry. By default,
                      only the latest published version for each entry is
                      retrieved.
  --output-file FILE  Path to the JSON file where the obtained record's
                      metadata will be exported to.  [required]
  --help              Show this message and exit.
```

### Create records

```bash
bma record create --help
```

```text
Usage: bma record create [OPTIONS]

  Create a record on a BIG-MAP Archive and optionally publish it.

Options:
  --config-file FILE      Path to the YAML file that specifies the domain name
                          and a personal access token for the targeted BIG-MAP
                          Archive. See bma_config.yaml in the GitHub
                          repository.  [required]
  --metadata-file FILE    Path to the YAML file for the record's metadata
                          (title, list of authors, etc). See
                          data/input/example/create_record/metadata.yaml in
                          the GitHub repository.  [required]
  --data-files DIRECTORY  Path to the directory that contains the data files
                          to be uploaded and linked to the record. See
                          data/input/example/create_record/upload in the
                          GitHub repository.  [required]
  --publish               Publish the created record.
  --help                  Show this message and exit.
```

### Update records

```bash
bma record update --help
```

```text
Usage: bma record update [OPTIONS]

  Update a published version of an archive entry, or create a new version and
  optionally publish it. When updating a published version, only the metadata
  (title, list of authors, etc) can be modified.

Options:
  --config-file FILE              Path to the YAML file that specifies the
                                  domain name and a personal access token for
                                  the targeted BIG-MAP Archive. See
                                  bma_config.yaml in the GitHub repository.
                                  [required]
  --record-id TEXT                Id of the published version (e.g.,
                                  "pxrf9-zfh45").  [required]
  --update-only                   Update the metadata of the published
                                  version, without creating a new version. By
                                  default, a new version is created.
  --metadata-file FILE            Path to the YAML file that contains the
                                  metadata (title, list of authors, etc) for
                                  updating the published version or creating a
                                  new version. See data/input/example/update_r
                                  ecord/metadata.yaml in the GitHub
                                  repository.  [required]
  --data-files DIRECTORY          Path to the directory that contains the data
                                  files to be linked to the newly created
                                  version. See
                                  data/input/example/update_record/upload in
                                  the GitHub repository.  [required]
  --link-all-files-from-previous  Link all files that are already linked to
                                  the previous version to the new version,
                                  with the exception of files whose content
                                  changed.
  --publish                       Publish the newly created version.
  --help                          Show this message and exit.
```

### Back up FINALES databases

```bash
bma finales-db back-up --help
```

```text
Usage: bma finales-db back-up [OPTIONS]

  Back up the SQLite database of a FINALES server to a BIG-MAP Archive. This creates and publishes a new entry version, which provides links to data extracted from the database (capabilities, requests, and results for requests) and a copy of the whole database.
Options:
  --bma-config-file FILE          Path to the YAML file that specifies the
                                  domain name and a personal access token for
                                  the targeted BIG-MAP Archive. See
                                  bma_config.yaml in the GitHub repository.
                                  [required]
  --finales-config-file FILE      Path to the YAML file that specifies the IP
                                  address, the port, and the credentials of a
                                  user account for the targeted FINALES
                                  server. See finales_config.yaml in the
                                  GitHub repository.  [required]
  --record-id TEXT                Id of the published version for the previous
                                  back-up (e.g., "pxrf9-zfh45"). For the first
                                  back-up, leave to the default.
  --metadata-file FILE            Path to the YAML file that contains the
                                  metadata (title, list of authors, etc) for
                                  creating a new version. See data/input/examp
                                  le/create_record/metadata.yaml in the GitHub
                                  repository.  [required]
  --link-all-files-from-previous  Link all files that are already linked to
                                  the previous version to the new version,
                                  with the exception of files whose content
                                  changed.
  --no-publish                    Do not publish the newly created version.
                                  This is discouraged in production. If you
                                  select this option, either publish or delete
                                  the newly created draft, e.g., via the GUI.
  --help                          Show this message and exit.
````

While executing the command, a user will be asked for confirmation if:
- The user attempts to create an entry (i.e., no record id is provided) but he/she already owns a published record with the same title. This is to prevent users from creating new entries inadvertently. 
- The user tries to update an existing entry (a record id is provided) but the new version would have a different title. This is to enforce our 'one title per "campaign"' policy (see [Back-up policy for FINALES databases](#back-up-policy-for-finales-databases))

When backing up a production database, put the corresponding `metadata.yaml` file under version control in the [big-map-archive-api-client-finales](https://github.com/materialscloud-org/big-map-archive-api-client-finales) GitHub repository. 

## Back-up policy for FINALES databases

The following back-up policy applies to the database of FINALES servers in production:
- There should be a single entry in the main BIG-MAP Archive per "campaign" on the FINALES server.
- An entry may have multiple versions, with one version created and published each time a back-up of the database occurs. Note that if a data file remains unchanged from one version to the next, the file is uploaded only once. However, the corresponding file link appears in the two entry versions. This saves storage space and reduces back-up time. 
- A title is given to each version of an entry. It can be changed but, since it serves as an identifier of the campaign, should ideally remain unchanged across all versions of the same entry. To enforce this 'one title per "campaign"' policy, the command `bma finales-db back-up` asks for confirmation if the user attempts to change the title while creating a new version. 
- A single service account is used for doing back-ups of a given "campaign".
- The same service account can be used for multiple "campaigns".

## Support

If you have any comments or questions, email us at big-map-archive@materialscloud.org.

## Issue

If you find a bug, please create an issue directly into [GitHub](https://github.com/materialscloud-org/big-map-archive-api-client/issues). If possible, give enough details so that the BIG-MAP Archive team is able to reproduce the encountered problem. Thank you!

## Acknowledgements

This project has received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189). The project is part of BATTERY 2030+, the large-scale European research initiative for inventing the sustainable batteries of the future.



