
# Artifacts for ACM CCS 2026 Paper #4517

This repository contains the experimental artifacts and result datasets for the paper:  
**"ECH in Practice: Deploying Privacy Protections over Insecure DNS"**

## Overview
This artifact provides the complete set of daily experiment outputs and a consolidated 10GB archive for reproducibility.

## Data Structure
- `results/`: Contains individual zipped results for each experiment day (e.g., `2026-04-29-results-top1M-GV97K.zip`). These are tracked via **Git LFS** to manage large file sizes within the repository history.
- **Official Release (v1.0)**: For users requiring the full consolidated dataset (~10GB), a single archive named `results.zip` is available under the [https://github.com/thedeep28/ACM_CCS2026_4517_Artifacts/releases/tag/v1.0] tab.

## Hardware & Software Requirements
*   **Storage**: At least 10GB of free space is required to extract the full dataset.
*   **Tools**: `unzip` or any standard archive manager.
*   **Git LFS**: To clone this repository with the daily result files, you must have [Git Large File Storage](https://git-lfs.github.com/) installed.

## Getting Started
To clone this repository and retrieve the results in the `results/` folder:
```bash
git lfs install
git clone https://github.com
```

## Anonymity & Open4Science
This repository is configured for use with [https://anonymous.4open.science/r/ACM_CCS2026_4517_Artifacts-6565/] for double-blind peer review. The use of Git LFS ensures that the file tree remains navigable even when anonymized.
