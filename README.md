# GitHubArchiver
Downloads every GitHub repository of an account, for archiving purposes.

## API token
Upon execution, this script will ask an API token. This can be created in the settings under *Personal Access Tokens*. This script requires at least the `repo`-scope.

## Run
```shell script
python3 main.py github_api output_directory
```

### Example

```shell script
python3 main.py https://api.github.com /tmp/repositories
```

```shell script
python3 main.py https://github.ugent.be/api/v3 /tmp/repositories
```