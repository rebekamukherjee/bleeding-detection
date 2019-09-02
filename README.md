# Bleeding Detection

This repository contains python scripts used in the study at The University of Utah Department of Cardiovascular Medicine to detect bleeding events among patients using natural language processing.

## Directory Structure

```
bleeding-detection
|
+-- src
|	|
|	+-- data
|	|
|	+-- results
|	|
|	+-- extract.py
|
|
+-- README.md
```

## Method

### Usage

To extract clinical notes without noise from the training (-t) or validation (-v) metadata, run the following command on CLI:

```
python extract.py [-t | -v] <phrase_length>
```