# KLayout Components Library

A collection of reusable KLayout components, parametric generators, PCells, and Python macros for microfluidic and microsystem layout design.

## What this repository provides

This repository is intended as a reusable component library for KLayout. Depending on the file, components may be provided as:

- Python macros (`.py`)
- KLayout macros (`.lym`)
- PCells packaged inside Python or Ruby scripts
- Example layouts and test cells
- Documentation and usage notes

The recommended installation method depends on how you want to use the library.

## Installation options

### Option 1: Use the repository directly from your KLayout macros folder

This is the simplest approach if you want the components to appear directly in your local KLayout setup.

1. Locate your KLayout user macros directory.

Typical locations are:

- macOS: `~/.klayout/pymacros/`
- Linux: `~/.klayout/pymacros/`
- Windows: `%USERPROFILE%\\KLayout\\pymacros\\` or the corresponding KLayout user macro folder

2. Clone this repository into that folder, or copy the relevant files into it.

Example:

```bash
git clone <your-repo-url> ~/.klayout/pymacros/klayout-components
```

3. Restart KLayout.

4. Open **Tools -> Macro Development IDE** to verify that the macros are visible.

If the repository contains subfolders, KLayout will keep that structure inside the macro browser.

### Option 2: Keep the repository anywhere and create a symbolic link

This is convenient if you want to version-control the repository in a normal development folder while still exposing it to KLayout.

1. Clone the repository anywhere you like, for example:

```bash
git clone <your-repo-url> ~/dev/klayout-components
```

2. Create a symbolic link inside KLayout's macro directory:

```bash
ln -s ~/dev/klayout-components ~/.klayout/pymacros/klayout-components
```

3. Restart KLayout.

This approach is usually the best one for active development because edits in the repository are immediately reflected in the linked macro folder.

### Option 3: Copy only selected components

If you only want a few components:

1. Copy the relevant `.py` or `.lym` files into your KLayout user macro directory.
2. Restart KLayout.
3. Run the macros manually from the macro browser or from the Macro Development IDE.

This is a good option if you want a lightweight setup without the full library.

## Installing PCells and reusable libraries

Some components may be implemented as PCells rather than standalone macros.

In that case, the usual workflow is:

1. Place the script file in the KLayout macro directory.
2. Start KLayout.
3. Run the library-registration macro once if required.
4. Open the **Libraries** panel or the **PCell insertion** dialog.
5. Insert the component from the registered library.

If a component does not appear automatically, check whether the script must be executed once to register a library class.

## Updating the library

To update the installed components:

### If you cloned the repository

```bash
cd ~/.klayout/pymacros/klayout-components
git pull
```

### If you use a symbolic link

Update the original repository:

```bash
cd ~/dev/klayout-components
git pull
```

Then restart KLayout to reload the macros.

## Recommended repository structure

A practical structure for this type of library is:

```text
klayout-components/
├── README.md
├── components/
│   ├── channels/
│   ├── mixers/
│   ├── junctions/
│   └── utilities/
├── pcells/
├── examples/
├── tests/
└── docs/
```

You can mirror this structure inside `~/.klayout/pymacros/` so the macro browser stays organized.

## How to use the components in KLayout

Depending on the implementation, components may be used in one of three ways:

- **Run as a macro**: launch the script from the Macro IDE or macro browser.
- **Insert as a PCell**: choose the registered library component from KLayout's PCell tools.
- **Import as a helper module**: call shared functions from your own KLayout scripts.

For Python-based components, a common pattern is:

```python
import pya
from components.channels.serpentine import make_serpentine
```

This requires the repository to be inside KLayout's Python macro search path, which is why installing it in `pymacros` (or linking it there) is recommended.

## Troubleshooting

### The macros do not appear in KLayout

- Confirm the files are inside the correct KLayout macro folder.
- Confirm the files have the correct extension (`.py` or `.lym`).
- Restart KLayout after installation.
- Open the Macro Development IDE and check whether the files are listed.

### A component does not appear as a PCell

- The library may need to be registered by running a setup macro once.
- Check for errors in the KLayout console.
- Make sure the file defining the library is actually loaded.

### Imports fail between modules

- Keep the repository inside `~/.klayout/pymacros/` or symlink it there.
- Preserve the folder structure.
- Make sure package folders include `__init__.py` files if needed for your Python version and organization.

## Development notes

For active development, the symbolic-link workflow is usually the most convenient because it allows:

- normal Git usage,
- clean repository organization,
- immediate editing with your preferred editor,
- direct availability inside KLayout.

## Requirements

- KLayout with Python macro support enabled
- Git (recommended, for installation and updates)

## License

See `license.md` (or your chosen repository license file) for licensing terms.
