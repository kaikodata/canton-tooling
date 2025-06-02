# Canton Templating Script

The `canton-templating.py` script processes template files and directories, replacing environment variables, creating symlinks for renamed directories, and generating `.gitignore` entries for those symlinks. It is designed for use with Canton-related Kubernetes deployments, supporting variable substitutions, Chart.yaml alias prefixing, and Git integration.

## Prerequisites

To use the script, ensure the following are installed:

- **Python 3.6+**: The script uses Python 3 features and standard libraries.
- **PyYAML**: Required for parsing YAML files. Install with:
  ```bash
  pip install pyyaml
  ```
- **Git**: Optional, for `--use-gitignore` to update the repository’s `.gitignore`.
- A **template directory** (e.g., `canton-sv-template/`) containing files and directories with placeholders (e.g., `MIGRATION_ID`, `ENVIRONMENT`).
- An **environment file** (e.g., `canton-envs/canton-sv-devnet1.txt`) with key-value pairs for substitutions (e.g., `ENVIRONMENT=canton-sv-devnet1`).

## Usage

Run the script from the command line, providing the required arguments and optional flags:

```bash
./canton-templating.py <src_dir> <dest_dir> <env_file> [--debug] [--alias-prefix] [--use-gitignore]
```

- **`<src_dir>`**: Path to the template directory (e.g., `canton-sv-template/`).
- **`<dest_dir>`**: Path to the output directory (e.g., `canton-sv-devnet1/`).
- **`<env_file>`**: Path to the environment file with variable definitions (e.g., `canton-envs/canton-sv-devnet1.txt`).

### Command-Line Arguments

#### Mandatory Arguments
- `src_dir`: Source directory containing templates.
- `dest_dir`: Destination directory for processed templates.
- `env_file`: File containing environment variables (key-value pairs, e.g., `KEY=VALUE`).

#### Optional Arguments
- `-h`, `--help`: Show the help message and exit.
- `--debug`: Enable debug logging for string substitutions (default: `False`).
  - Logs variable replacements in file content and filenames (e.g., `#nodeId: ...` → `nodeId: ...`).
- `--alias-prefix`: Enable alias prefixing and reindentation in YAML files (default: `False`).
  - Adds a prefix (e.g., `cometbft:`) from `Chart.yaml` dependencies to YAML files, excluding `Chart.yaml`, `Chart.yml`, and `values.yaml`.
- `--use-gitignore`: Update the Git repository’s `.gitignore` instead of creating one in `dest_dir` (default: `False`).
  - Appends symlink paths (e.g., `canton-sv-devnet1/scan/ENVIRONMENT`) to the repo’s `.gitignore`.
  - Falls back to `dest_dir/.gitignore` if no Git repo is found.

If an invalid parameter is provided (e.g., `--invalid-flag`), the script displays the help message and exits.

## Features

- **Variable Substitutions**:
  - Replaces placeholders in file content and filenames with values from the environment file.
  - Supports `#`-containing variables (e.g., `#nodeId: ...` → `nodeId: ...`) with debug logging.
  - Skips substitution if a `#` precedes the variable (e.g., `# nodeId: NODE_ID#1` remains unchanged).

- **Symlink Creation**:
  - Creates symlinks for directories renamed due to variable substitution (e.g., `scan/ENVIRONMENT` → `scan/canton-sv-devnet1`, symlink: `scan/ENVIRONMENT -> canton-sv-devnet1`).
  - Cleans up existing symlinks before processing to prevent nesting across multiple runs.

- **`.gitignore` Generation**:
  - **Default**: Creates `dest_dir/.gitignore` with symlink paths (e.g., `scan/ENVIRONMENT`).
  - **With `--use-gitignore`**: Appends paths to the Git repository’s `.gitignore`, relative to the repo root.
  - Paths have no trailing slashes for correct Git behavior.

- **Chart.yaml Alias Prefixing**:
  - With `--alias-prefix`, adds a prefix (e.g., `cometbft:`) from `Chart.yaml` dependencies to YAML files (excluding `Chart.yaml`, `Chart.yml`, `values.yaml`) and reindents content.

## Examples

### Basic Usage
Process templates without optional flags:

```bash
./canton-templating.py canton-sv-template/ canton-sv-devnet1/ canton-envs/canton-sv-devnet1.txt
```

- Creates `canton-sv-devnet1/.gitignore` with symlink paths (e.g., `scan/ENVIRONMENT`).
- No debug logs, no alias prefixing in YAML files.

### With Debug Logging and Alias Prefixing
Enable debug logging and alias prefixing:

```bash
./canton-templating.py canton-sv-template/ canton-sv-devnet1/ canton-envs/canton-sv-devnet1.txt --debug --alias-prefix > output.txt 2>&1
```

- Debug logs in `output.txt` for substitutions (e.g., `#nodeId: ...` → `nodeId: ...`).
- YAML files (e.g., `participant-values.yaml`) include alias prefix (e.g., `cometbft:`) and reindentation.
- Creates `canton-sv-devnet1/.gitignore`.

### Using Git Repository’s `.gitignore`
Update the Git repo’s `.gitignore`:

```bash
./canton-templating.py canton-sv-template/ canton-sv-devnet1/ canton-envs/canton-sv-devnet1.txt --use-gitignore
```

- Appends paths (e.g., `canton-sv-devnet1/scan/ENVIRONMENT`) to the repo’s `.gitignore` (e.g., `/home/user/project/.gitignore`).
- No `canton-sv-devnet1/.gitignore` created unless no Git repo is found.

### Invalid Parameter
Test an invalid flag:

```bash
./canton-templating.py canton-sv-template/ canton-sv-devnet1/ canton-envs/canton-sv-devnet1.txt --invalid-flag
```

- Displays help message with mandatory/optional arguments and exits.

## Bad Things Needed

[Placeholder for you to fill in with any known issues, limitations, or dependencies that need attention.]

## Troubleshooting

- **No `.gitignore` Created**: Ensure `dest_dir` is writable. If using `--use-gitignore`, verify a Git repository exists (contains a `.git` directory).
- **Nested Symlinks**: Should not occur due to symlink cleanup. If seen, share `find canton-sv-devnet1/ -type l | xargs ls -ltr` output.
- **Substitution Issues**: Check the environment file for correct key-value pairs. Use `--debug` to log substitutions.
- **Invalid Parameters**: Run with `--help` to see available arguments.

For issues, share:
- Debug logs (`output.txt` from a run with `--debug`).
- `ls -lR <dest_dir>` output.
- `canton-sv-template/` directory structure.
- Environment file contents.

## License

(c) Kaiko 2025 ...
Do what you want with that script. It was mostly entirely generated from Grok using my newly discovered "Promp Eng" skills.
I'd prefer to have PR than just bug reports or suggestions of course ;)
It fits my needs, it could fit yours directly or with a few modifications

## Who/What it is intended for

People that deploy or maintain Validator or Super Validator nodes on Canton.
Either initial deployment or weekly updates
Also includes major upgrades like 0.3.1 => 0.4.0 with MIGRATION_ID bumped
Makes sure you don't forget to update a variable
Makes sure you can keep in sync your variables with latest provided values.yaml from newer splice bundle.
Could be also useful for SV operators as it could generate double-run deployments (for components which are deployed twice during a migration)

## The not so good

Part of that script could go away/be simplified if a few things were changed in splice provided example values.yaml files :
*   hardcoded values like svNamespace: "sv" or svNamespace: "validator"
*   variables with no values (even a PLACE_HOLDER) that only contains a comment like # Please provide a value as provided in the docs
*   2 blocks, 1 to uncomment depending on network (for sv, nodeId, publicKey, keyAddress)

For the second one, a file containing amuletName, amuletNameAcronym, ... or simply adding fake place-holders like other variables (AMULET_NAME_ACRONYM, ...)

For the third one, 2 files, one containing devnet/testnet values or simply adding fake place-holders like other variables (SV_NODE_ID, SV_PUBLIC_KEY, ...)
