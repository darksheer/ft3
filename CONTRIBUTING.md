# Contributing

Contributions of any kind are welcome! If you've found a bug or have a feature request, please feel free to [open an issue](/issues). 

<!-- We will try and respond to your issue or pull request within a week. -->

To make changes yourself, follow these steps:

1. [Fork](https://help.github.com/articles/fork-a-repo/) this repository and [clone](https://help.github.com/articles/cloning-a-repository/) it locally.
2. Create a Python 3.12 environment with `python3.12 -m venv .venv`, then install the public YAML dependency with `.venv/bin/python -m pip install -r requirements.txt`.
3. Edit the appropriate record under `catalog/tactics/` or `catalog/techniques/`. Add or remove an ID in `catalog/order.yaml` only when the reviewed catalog change requires it. The four root JSON/CSV catalogs are generated files.
4. Run `.venv/bin/python -m ft3_tools build`, `.venv/bin/python -m unittest discover -s tests -v`, and `.venv/bin/python -m ft3_tools check`.
5. Include both the YAML and generated-file changes in your [pull request](https://help.github.com/articles/creating-a-pull-request-from-a-fork/). Explain any change to the field contract, IDs, order, or the exact known-reference exceptions.

## Contributor License Agreement ([CLA](https://en.wikipedia.org/wiki/Contributor_License_Agreement))

Once you have submitted a pull request, sign the CLA by clicking on the badge in the comment from [@CLAassistant](https://github.com/CLAassistant).

<img width="910" alt="image" src="https://user-images.githubusercontent.com/62121649/198740836-70aeb322-5755-49fc-af55-93c8e8a39058.png">

<br />
Thanks for contributing to Stripe! :sparkles:
