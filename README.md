# BAMBOO

[![Python](https://img.shields.io/badge/Python-3776AB.svg?logo=Python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626.svg?logo=Jupyter&logoColor=white)](https://jupyter.org/)
[![License](https://img.shields.io/github/license/Annedrew/bamboo?color=5D6D7E)](https://github.com/Annedrew/bamboo/blob/main/LICENSE)

This is a Python package designed to import external input-output databases to brightway, such as EXIOBASE. In addition, it can assist you to model different types of uncertainty analysis or scenario analysis with datapackage matrix data.  

This library is developed based on **[Brightway2.5](https://docs.brightway.dev/en/latest/)** and **[EXIOBASE3](https://www.exiobase.eu/index.php/9-blog/31-now-available-exiobase2)** dataset.

## 📖 Background Knowledge 

### EXIOBASE
[EXIOBASE](https://www.exiobase.eu/) is a global, detailed Multi-Regional Environmentally Extended Supply-Use Table (MR-SUT) and Input-Output Table (MR-IOT). It can be used to do Life Cycle Assessment(LCA) analysis. The inventory data and emission data is stored in `txt` files. 

[EXIOBASE3](https://zenodo.org/records/3583071) is one of the most extensive EE-MRIO systems available worldwide. EXIOBASE 3 builds upon the previous versions of EXIOBASE by using rectangular supply‐use tables (SUT) in a 163 industry by 200 products classification as the main building blocks.

### Formula

$g = B (I-A)^{-1} f$. 

Where:
- B: Biosphere matrix
- A: Technospere matrix
- I: Identity matrix
- $f$: Functional unit
- g: Inventory

## ✨ Features
- Perform LCA based on input-output databases (such as EXIOBASE), using Brightway.
  - Perform LCA using only EXIOBASE as background system, or using EXIOBASE combined with a customizable foreground system.
    - The corresponding matrices are arranged like this:  
    The foreground system is constructed from four matrices: `fgbg`, `fgfg`, `bgfg`, and `bifg`. These matrices are named to reflect their row and column positions. Specifically:
      - `fgfg`: This is the square matrix representing the foreground system. It includes exchanges from foreground (fg) to foreground (fg).
      - `fgbg`: This is the matrix representing all exchanges from the foreground (fg) system to the background (bg) system. Normally, this matrix is empty because the background system (database) is pre-defined and thus does not have inputs form the user-defined foreground system. So, by default this matrix is all zeros.
      - `bgfg`: This is the matrix representing all exchanges from the background (bg) to the foreground (fg) system. For example, this could be the input of “EU28-Energy” to an activity in the foreground system.
      - `bifg`: This is the matrix representing all the biosphere (bi) exchanges in the foreground (fg) system.  
    ![matrices figure](./assets/matrices_figure.png)
- Uncertainty Analysis for input-output databases.
  - `uniformly`: This strategy assumes that all exchanges have the same uncertainty(that is type of distribution, location, and scale). It adds this uncertainty information to all exchanges to both biosphere and technosphere matrices or the user can specify to add uncertainty only to one of them.
  - `columnwise`: This strategy adds the same uncertainty information to each exchange of a specific column of a matrix, but different uncertainty information to each column of a matrix. Different columns can thus have different uncertainty(that is type of distribution, location, and scale). To use this strategy, the uncertainty information should be defined in the user input file ([foreground_system_2.csv](notebooks/data/foreground_system_2.csv)).
  - `itemwise`: This strategy adds different uncertainty(that is type of distribution, location, and scale) to different exchanges. To use this strategy, the uncertainty information should be defined in the user input file ([foreground_system_2.csv](notebooks/data/foreground_system_2.csv)).

  **NOTICE:**  
    - Supported uncertainty type: 0, 1, 2, 3, 4 (Check [here](https://stats-arrays.readthedocs.io/en/latest/#mapping-parameter-array-columns-to-uncertainty-distributions) to select your uncertainty type.)
    - For strategy 2) and 3), only technosphere and biosphere matrices are supported.
    - `itemwise` recommends apply only to the foreground system, considering the amount of data that introduces uncertainty for both systems. The library does not specifically handle this situation.

## 👩‍💻 Getting Started
### Requirements
- This library was developed using **Python 3.12.9**.

### Dependencies

- To use this library, you have to have **Brightway2.5** installed. (To install Brightway, click [here](https://docs.brightway.dev/en/latest/content/installation/)).
- If you need to find the characterization factors through Brightway, then you need to have ecoinvent imported, otherwise, it is not necessary.
  - If you have ecoinvent license, click [here](https://docs.brightway.dev/en/latest/content/cheatsheet/importing.html) to see how to import.
  - If you don't have ecoinvent license:
    ```
    bi.remote.install_project('<project_tag>', '<my_desired_project_name>')
    ```
    - Where `<project_tag>` is one of:
      - `ecoinvent-3.10-biosphere`
      - `ecoinvent-3.8-biosphere`
      - `ecoinvent-3.9.1-biosphere`
      - `forwast`
      - `USEEIO-1.1`

### Installation
1. Open your local terminal.  
(For windows, search for "Terminal/Prompt/PowerShell"; for macOS, search for "Terminal")

2. Install the library.
   ```
   pip install bamboo_lca
   ```

### Required files
(The examples of those file is in [data](notebooks/data) folder.)
- **External database file**: This is the file of your background database, for example the `A.txt` and `S.txt` for EXIOBASE.
- **Foreground system file**: This is the file for your foreground database, you need to prepare yourself. 
  - Reference examples: 
    - [foreground_system_1.csv](notebooks/data/foreground_system_1.csv)
    - [foreground_system_2.csv](notebooks/data/foreground_system_2.csv). 
  - Below shows the purpose of each column. You only need to change the data instead of the column names and order. 
    - Activity name: includes all activity names of foreground.
    - Exchange name: includes all exchange names of foreground.
    - Exchange type: indicate the exchange is belongs to technosphere, biosphere or production.
    - Exchange amount: indicate the amount of exchange required.
    - Exchange uncertainty type: indicate the type of uncertainty you are gonna experiment. (Check uncertainty types [here](https://stats-arrays.readthedocs.io/en/latest/#mapping-parameter-array-columns-to-uncertainty-distributions)).
    - GSD: short for "Geometric Standard Deviation", used for uncertainty distribution definition.
    - Exchange negative: indicate uncertainty distribution is negative or positive.

- **Characterization factor file**: 
  - Below shows the purpose of some columns. 
    - brightway code: This is the code of activity in Brightway. 
    - CFs: The characterization factor value.
### Notebooks
- [LCA with imported external database](https://github.com/Annedrew/brightway-bamboo/blob/main/notebooks/lca_with_foreground.ipynb)
- [LCA with background database](https://github.com/Annedrew/brightway-bamboo/blob/main/notebooks/lca_with_background.ipynb)
- [Uncertainty analysis](https://github.com/Annedrew/brightway-bamboo/blob/main/notebooks/uncertainty_analysis.ipynb)

### Figures
There are some figures in the [assets](assets) folder to help you understand the structure of the library.

## 💬 Contact
If you encounter any issues or would like to contribute to the library, please contact: 
  - Ning An (ningan@plan.aau.dk)
  - Elisabetta Pigni (elisabetta.pigni@unibo.it)
  - Massimo Pizzol (massimo@plan.aau.dk)
