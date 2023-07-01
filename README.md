# Key Value store with raft consensus algorithm

## Setup

```bash
git clone https://github.com/notarisj/raft.git
```

```bash
cd raft
```

Generate the distribution package (optional)
```bash
python3 setup.py sdist
```

```bash
pip install dist/raft*.tar.gz
```

## Usage

### Update configuration file

Before running the application, you need to update the [config.ini](src/configurations/config.ini) file. You may 
generate a certificate and key (see command bellow), or use the ones provided, and also update the paths for the 
properties `ssl_cert_file` and `ssl_key_file` in the configuration file. You can also change the API credentials 
and MongoDB settings here.

### Running Raft Application
You can start the server using the [run_server.sh](help_scripts/run_raft_server.sh) bash script. This script takes some 
optional arguments for configuration. If no parameters are provided,
the script will use the default configuration from the [config.ini](src/configurations/config.ini) 
and [servers.json](src/configurations/servers.json) file. Note that if you want to test it in the same machine, you 
need to pass `--server_id` and `--mongo_collection_name` arguments for each node as seen in the example usage bellow.

Install mongodb (if not installed)
```bash
./help_scripts/install_mongodb.sh
```

#### Start the server:
```bash
./help_scripts/run_raft_server.sh [options]
```

The `directory_path` is the path to the directory of the project. You can use `.` if 
you are in the root directory of the project as follows:

#### Example usage:
```bash
./help_scripts/run_raft_server.sh --server_id 1 --mongo_collection_name raft1
```

#### Options:

- `--server_id <server_id>`
- `--uvicorn_host <uvicorn_host>`
- `--uvicorn_port <uvicorn_port>`
- `--mongo_host <mongo_host>`
- `--mongo_port <mongo_port>`
- `--mongo_db_name <mongo_db_name>`
- `--mongo_collection_name <mongo_collection_name>`


Please refer to the [run_server.sh](help_scripts/run_raft_server.sh) script for 
more details.

### Running Key Value Store Application

#### Start the server
```bash
./help_scripts/run_kv_server.sh [options]
```

#### Example usage

```bash
./help_scripts/run_kv_server.sh --server_id 1 --replication_factor 2
```

#### Options:

- `--server_id <server_id>`
- `--replication_factor <replication_factor>`

### Running the command line interfaces

With the raft and key value store servers running, you can use the command line interfaces to start the cluster and 
start interacting with the store.

#### Raft CLI
```bash
./help_scripts/run_raft_cli.sh
```
For more information see [Raft CLI](src/raft_node/cli/README.md)

#### Key Value Store CLI
```bash
./help_scripts/run_kv_cli.sh
```
For more information see [Key Value Store CLI](src/kv_store/cli/README.md)

## Running tests

To run the tests execute the following command:
```bash
./help_scripts/run_tests.sh
```

## Generate SSL certificate for th API
```bash
openssl req -newkey rsa:2048 -nodes -keyout private_key.pem -x509 -days 365 -out certificate.pem -subj "/CN=localhost" -addext "subjectAltName = IP:127.0.0.1, DNS:localhost"
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
