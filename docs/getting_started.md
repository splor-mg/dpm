## Getting Started with Data Package Manager (DPM)

To get started with the Data Package Manager, you can install it using:

```bash
pip install dpm
```

DPM simplifies the process of installing (downloading) data resources described in [Frictionless data package](https://specs.frictionlessdata.io/data-package/) descriptors and provides a set of functionalities to manage them.

If you have a valid data package descriptor, such as a `datapackage.json` file, you can use the command `dpm install` to download its data sources in a structured way to your local machine.

### Step 1: Create a Configuration File

Begin by creating a file named `data.toml` in the root of your project, containing the metadata for the data packages you want to use:

```toml
# file: data.toml
[packages]

[packages.your_datapackage_name]
path = "https://raw.githubusercontent.com/your-org/your_repo/datapackage.json"
token = "your_github_pat_if_needed_to_access_private_repositories"
```

### Step 2: Install the Data Packages

Next, run the following command:

```bash
dpm install
```

This command will access the `datapackage.json` located at the specified URL in your `data.toml` file. The resources described in the `datapackage.json` will be downloaded and saved in the `datapackages` folder by default.

For each resource, a subfolder named `your_datapackage_name` will be created, and the data package descriptor will also be downloaded:

```plaintext
.
└── your_project_name/
    ├── datapackages/
    │   ├── your_datapackage_name/
    │   │   ├── resource1.csv
    │   │   └── resource2.xlsx
    │   └── datapackage.json
    ├── README.md
    ├── data.toml
    └── main.py
```
