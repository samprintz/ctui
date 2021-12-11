# rdf-contact-tui

Text-based user interface for managing contacts.
Inspired by [ranger](https://en.wikipedia.org/wiki/Ranger_(file_manager)).
Contact data is stored in RDF/N3 file.
Notes can be managed in text files.

## Installation

### Create encryption key

1. Run <code>gpg --full-generate-keys</code> and follow the dialog
2. Run <code>gpg --list-keys --keyid-format long</code> to get the key ID. The key are in place of the bold "X" in an output similar to this:

```bash
pub   rsa3072/<b>XXXXXXXXXXXXXXXX<b> 2021-09-01 [SC]
      XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
uid              [ ultimativ ] Your Name (Some comment) <e-mail@address.com>
sub   rsa3072/XXXXXXXXXXXXXXXX 2021-09-01 [E]
```

