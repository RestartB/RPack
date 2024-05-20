# RPack
Restart Package Manager

## Current Supported Features
### Essentials
- [X] Adding Repos
- [X] Removing Repos
- [X] Syncing Repos
- [X] Downloading Packages
- [ ] Updating Packages
- [ ] Uninstalling Packages

### Other
- [X] Multi-platform Support
- [X] Multi-arch Support

## Hosting a Repo
### Supported Features
#### Platforms
`win32` - Windows\
`darwin` - macOS\
`linux` - Linux
#### Package Architecture
`AMD64` - 64bit\
`aarch64` - Arm 64bit

Your repo must be hosting a `repo.json` file, with the following structure:
```
{
  "repo-name" : "Your Repo's Name",
  "repo-author" : "Repo Author's Name",
  "repo-country" : "Country Code (e.g. GB)",
  "packages" :
  {
      "Package Name (must be all one word)" : {
          "info" : {
              "fullName" : "Package Full Name",
              "description" : "Package Description",
              "author" : "Package Author",
              "latest" : "Latest Package Version"
          },
          "Package Platform" : {
              "Package Architecture" : {
                  "Package Version" : {
                      "sourceURL" : "Package Source URL",
                      "installCommand" : "Package Install Command (use {FILE} as placeholder for file)"
                  }
              }
          }
      }
  }
}
```
