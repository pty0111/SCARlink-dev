import os
import h5py
import glob
from scarlink.src.read_model import read_model

def get_coef_file(gene_list, gene):
    for coef_file in gene_list:
        if gene in gene_list[coef_file]: return coef_file
            
def get_scarlink_output(dirname):
    dirname = dirname + '/' if dirname[-1] != '/' else dirname
    out_dir = dirname + 'scarlink_out/'
    plot_dir = dirname + 'scarlink_plots/'
    os.makedirs(plot_dir, exist_ok=True)
    all_coef_files = glob.glob(out_dir + 'coefficients*.hd5')
    gene_list = {}
    for coef_file in all_coef_files:
        f = h5py.File(coef_file, mode = 'r')
        f_genes = list(f['genes/'].keys())
        f.close()
        gene_list[coef_file] = f_genes
    scarlink_out = {}
    scarlink_out['gene_list'] = gene_list
    scarlink_out['dirname'] = dirname
    scarlink_out['plot_dir'] = plot_dir
    scarlink_out['out_dir'] = out_dir
    return scarlink_out

def plot_scarlink_output(scarlink_out, genes, celltype, features_to_plot = None, plot_frags = False, to_save = True, plot_file = '', cmap = None, save_format='png', figsize=(17, 14), sort_gex=True, show_yticks=False, shap_cmap='Blues', pvals_cmap='Blues', cluster_order=[], plot_shap=True, bg_transparent=False):
    if isinstance(genes, str): genes = [genes]
    for gene in genes:
        coef_file = get_coef_file(scarlink_out['gene_list'], gene)
        path = '/'.join(__file__.split('/')[:-2]) + '/data/'

        rm = read_model(scarlink_out['out_dir'], out_file_name=coef_file.split('/')[-1])
        rm.gtf_file = path + rm.gtf_file.split('/')[-1]
        rm.plot_gene(rm, gene, groups=celltype, features_to_plot=features_to_plot, plot_frags=plot_frags, to_save=to_save, plot_file=plot_file, plot_dir=scarlink_out['plot_dir'], cmap=cmap, save_format=save_format, figsize=figsize, sort_gex=sort_gex, show_yticks=show_yticks, plot_shap=plot_shap, shap_cmap=shap_cmap, cluster_order=cluster_order, bg_transparent=bg_transparent)
