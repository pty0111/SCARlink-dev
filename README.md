# SCARlink

This repository contains the code for SCARlink described in the paper: **Single-cell multi-ome regression models identify functional and disease-associated enhancers and enable chromatin potential analysis** by Mitra, S *et al.*, 2024: [https://www.nature.com/articles/s41588-024-01689-8](https://www.nature.com/articles/s41588-024-01689-8)

Please visit [wiki](https://github.com/snehamitra/SCARlink/wiki) for details about installation and running SCARlink. [Tutorial notebook](https://github.com/snehamitra/SCARlink/blob/main/notebooks/tutorial.ipynb) describes how to run SCARlink on a small example dataset.

Single-cell ATAC+RNA linking (SCARlink) uses multiomic single-cell ATAC and RNA to predict gene expression from chromatin accessibility and predict regulatory regions. It uses tile-based chromatin accessibity data from a genomic locus (+/-250kb flanking gene body) and applies regularized Poisson regression to predict gene expression. The learned regression coefficients of the tiles are informative of regulatory regions in a gene-specific manner. The regression model by itself is cell-type-agnostic. Shapley values computed by grouping cells provide insight into the regulatory regions in a cell-type specific manner. Therefore, the trained regression model can be used multiple times to identify important tiles for different groupings without retraining.


<div align="center">
<img src="docs/model_outline.jpg" width=90%>
</div>


## Installation 

It is optional to install SCARlink in a conda environment that also has R packages Seurat v4 and ArchR installed. If you already have the R packages installed and want to run SCARlink without conda, jump directly to [step 2](https://github.com/snehamitra/SCARlink?tab=readme-ov-file#2-scarlink-installation) of installation. Alternatively, for Docker setup, jump to [step 3](https://github.com/snehamitra/SCARlink?tab=readme-ov-file#3-docker-setup).

#### 1. Conda setup

The following conda setup is linux compatible. For conda setup on Apple M1, visit [wiki](https://github.com/snehamitra/SCARlink/wiki/1.-Installation#12-apple-m1). To install SCARlink within conda, first create a conda environment:

``` python
conda create -n scarlink-env python=3.8
conda activate scarlink-env
```

Set the priority of conda channels

```
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
```

Install essential R packages<sup>*</sup>

```
conda install -c conda-forge r-seurat r-devtools r-biocmanager
conda install -c bioconda bioconductor-rhdf5 \
      	      	     bioconductor-genomeinfodbdata \
                     bioconductor-chromvar \
                     bioconductor-motifmatchr \
                     bioconductor-complexheatmap
```

Install ArchR in the conda environment inside R

``` r
devtools::install_github("GreenleafLab/ArchR", ref="master", repos = BiocManager::repositories())
```

#### 2. SCARlink installation

Download SCARlink from GitHub and install

```
git clone https://github.com/snehamitra/SCARlink.git
pip install -e SCARlink
```

#### 3. Docker setup

Skip steps 1 and 2 if you want to run SCARlink inside a Docker container. Visit [wiki](https://github.com/snehamitra/SCARlink/wiki/1.-Installation#4-docker-setup) for additional details. First install [Docker](https://docs.docker.com/get-docker/) and then run SCARlink inside container as follows

```
docker run -it --rm --memory=50g mitrasneha/scarlink:latest
```

## Usage

SCARlink requires preprocessed scRNA-seq (normalized counts) in a Seurat object and scATAC-seq (non-binary tile matrix) in ArchR object. The cell names in both the objects need to be identical. Please refer to the [example notebook](https://github.com/snehamitra/SCARlink_private/blob/main/notebooks/preprocessing_scRNA_scATAC.ipynb) for generating Seurat and ArchR objects.

#### 1. Preprocessing
Run `scarlink_preprocessing` to generate `coasssay_matrix.h5` to use as input to SCARlink.

```
scarlink_processing --scrna scrna_seurat.rds --scatac scatac_archr -o multiome_out
```

#### 2. Running locally
For small data sets with few genes, run SCARlink sequentially on the gene set in the same output directory `multiome_out`, as before, for all the remaining steps. Note that `celltype` needs to be present in either `scrna_seurat.rds` or `scatac_archr`.

```
scarlink -o multiome_out -g hg38 -c celltype
```

#### 2a. Running locally without cell type information during training and computing cell type scores afterwards
SCARlink can also be run without providing cell type information using `-c`. In that case SCARlink only computes the gene-level regression model and does not estimate cell-type-specific Shapley values. 

```
scarlink -o multiome_out -g hg38 
```

The cell-type-specific Shapley scores can be computed later on by running `scarlink` with the `-c` parameter. In that case the previously estimated gene-regression models are used.

```
scarlink -o multiome_out -g hg38 -c celltype
```

#### 2b. Running locally with different cell type grouping
SCARlink can be run again with a different cell type annotation. For example, more granular annotations. Both `celltype` and `celltype_granular` scores would be retained.

```
scarlink -o multiome_out -g hg38 -c celltype_granular
```

#### 2c. Running on cluster by parallelizing over gene set
To speed up computation, SCARlink can be run on a cluster in parallel. By default it parallelizes over 100 cores, `-np 100` when `-np` is not provided. 
```bash
scarlink -o multiome_out -g hg38 -c celltype -p $LSB_JOBINDEX
```

#### 3. Get FDR corrected gene-linked tiles
Get table with tile-level siginificance for each gene and celltype.
```bash
scarlink_tiles -o multiome_out -c celltype 
```

#### 4. Chromatin potential
Chromatin potential analysis can be performed after running steps 1 and 2. Please refer to [example notebook](https://github.com/snehamitra/SCARlink_private/blob/main/notebooks/chromatin_potential.ipynb).

#### 5. Plot SCARlink output
SCARlink can create visualizations for the chromatin accessibility around a gene (250kb upstream and downstream of the gene body) and the gene expression for a given gene, grouped by user-provided celltype. The visualizations can help understand the connection between the accessibility at tile-level to gene expression. Note that SCARlink can generate visualizations for different cell type groupings on the fly. Example visulizations are provided in a [notebook](https://github.com/snehamitra/SCARlink_private/blob/main/notebooks/output_visualization.ipynb). The visualizations can also be generated at the command line.
```bash
scarlink_tiles -o multiome_out -c celltype --genes GENE1,GENE2
```

<sup>*</sup> The manuscript version of SCARlink uses Seurat v4 and ArchR 1.0.2. The new Seurat v5 installation is also compatible with SCARlink.