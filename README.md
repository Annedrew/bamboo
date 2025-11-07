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
  1. **uniformly**
      - This strategy assumes that all exchanges have the same uncertainty(that is type of distribution, location, and scale). It adds this uncertainty information to all exchanges to both biosphere and technosphere matrices or the user can specify to add uncertainty only to one of them.
  2. **columnwise**
      - This strategy adds the same uncertainty information to each exchange of a specific column of a matrix, but different uncertainty information to each column of a matrix. Different columns can thus have different uncertainty(that is type of distribution, location, and scale). To use this strategy, the uncertainty information should be defined in the user input file ([uncertainty_file.csv](notebooks/data/uncertainty_file.csv)).
  3. **itemwise**
      - This strategy adds different uncertainty(that is type of distribution, location, and scale) to different exchanges. To use this strategy, the uncertainty information should be defined in the user input file ([uncertainty_file.csv](notebooks/data/uncertainty_file.csv)).

  **NOTICE:**  
    - Supported uncertainty type: 0, 1, 2, 3, 4 (Check [here](https://stats-arrays.readthedocs.io/en/latest/#mapping-parameter-array-columns-to-uncertainty-distributions) to select your uncertainty type.)
    - For strategy 2 and 3, only technosphere and biosphere matrices are supported.
    - `itemwise` recommends apply only to the foreground system, considering the amount of data that introduces uncertainty for both systems. The library does not specifically handle this situation.

## 👩‍💻 Getting Started
### Requirements
- This library was developed using **Python 3.12.9**.

### Dependencies
- You need to have **Brightway2.5** installed. (click [here](https://docs.brightway.dev/en/latest/content/installation/) to see how to install Brightway).
- If you need to find the characterization factors through Brightway, then you need to have **ecoinvent** imported, otherwise, it is not necessary. (click [here](https://docs.brightway.dev/en/latest/content/cheatsheet/importing.html) to see how to import ecoinvent.)

### Installation
1. Open your local terminal.  
(For windows, search for "Terminal/Prompt/PowerShell"; for macOS, search for "Terminal")

2. Install the library.
   ```
   pip install bamboo_lca
   ```

### Required files
(The examples of those file is in [data](notebooks/data) folder.)
1. **External database file**
    - This is the file of your background database. For EXIOBASE, it's the `A.txt` and `S.txt`.
2. **Foreground system file**
    - Reference example: [foreground_system.csv](notebooks/data/foreground_system.csv)
    - This is the file for your foreground database, you need to prepare yourself. 
    - Below shows the purpose of each column. You only need to change the data instead of the column names and order. 
      - **Activity name**: includes all activity names of foreground.
      - **Exchange name**: includes all exchange names of foreground.
      - **Exchange type**: indicate the exchange is belongs to technosphere, biosphere or production.
      - **Exchange amount**: indicate the amount of exchange required.
3. **Uncertainty file**
    - Reference example: [uncertainty_file.csv](notebooks/data/uncertainty_file.csv)
    - It's essentially the same as foreground system file, just add uncertainty information to the same file. You can also add it in foreground system file.
    - You only need to change the data instead of the column names and order. Except the columns required in foreground system file, you also need:
      - **Exchange uncertainty type**: indicate the type of uncertainty you are gonna experiment. (Check uncertainty types [here](https://stats-arrays.readthedocs.io/en/latest/#mapping-parameter-array-columns-to-uncertainty-distributions)).
      - **GSD**: short for "Geometric Standard Deviation", used for uncertainty distribution definition.
      - **Exchange negative**: indicate uncertainty distribution is negative or positive.

4. **Characterization factor file**
    - Reference example: [cf_mapping_file.csv](notebooks/data/cf_mapping_file.csv)
    - Below shows the purpose of some columns. 
      - **brightway code**: This is the code of activity in Brightway. 
      - **CFs**: The characterization factor value.
### Notebooks
- [1. lca_with_background.ipynb](notebooks/1.%20lca_with_background.ipynb)
- [2. lca_with_foreground.ipynb](notebooks/2.%20lca_with_foreground.ipynb)
- [3.1. lca_with_uniform_uncertainty.ipynb](notebooks/3.1.%20lca_with_uniform_uncertainty.ipynb)
- [3.2. lca_with_columnwise_uncertainty.ipynb](notebooks/3.2.%20lca_with_columnwise_uncertainty.ipynb)
- [3.2. lca_with_itemwise_uncertainty.ipynb](notebooks/3.3.%20lca_with_itemwise_uncertainty.ipynb)

### Figures
There are some figures in the [assets](assets) folder to help you understand the structure of the library.

## 💬 Contact
If you encounter any issues or would like to contribute to the library, please contact: 
  - Ning An (ningan@plan.aau.dk)
  - Elisabetta Pigni (elisabetta.pigni@unibo.it)
  - Massimo Pizzol (massimo@plan.aau.dk)

## Funding
This contribution is funded by the ALIGNED project (Horizon Europe, grant number 101059430).
