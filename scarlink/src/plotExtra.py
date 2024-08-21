# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
import seaborn
# import pysam
import pandas
import random
plt.rcParams['text.usetex'] = False

def plotFeatures(features_to_plot, feature_name, chrm, start, end, ax, feature_color = "black"):
    """Plot features.
    
    Parameters
    ----------
    features_to_plot : pandas dataframe (0: chrm, 1: start, 2: end, 3: name)
    feature_name: str
        Name of the feature.
    chrm : str
        Chromosome number.
    start : int
        Start coordinate.
    end : int
        End coordinate.
    ax : axis
        Axis to plot on.
    """
    features_p = features_to_plot[(features_to_plot[0] == chrm) & 
                                  (features_to_plot[1] <= end) & (features_to_plot[2] >= start)]
    
    for i, r in features_p.iterrows():
        ax.add_patch(patches.Rectangle((r[1], 0.1), r[2] - r[1] + 1, 1.2, color = feature_color))
        if len(r) > 3:
            ax.text(r[1]-500, 1.5, '$\it{'+r[3]+'}$')
    ax.set_xlim((start, end))
    ax.set_ylim((-0.2, 1.3))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel(feature_name, fontsize=10, rotation=0, ha = "right")
    ax.spines['top'].set_visible(False) # new
    ax.spines['right'].set_visible(False) # new
    ax.spines['left'].set_visible(False) # new
    ax.spines['bottom'].set_visible(False) # new

def plotRegion(chrm, start, end, ax, gtf_file):
    """Plot gene annotations.
    
    Parameters
    ----------
    chrm : str
        Chromosome number.
    start : int
        Start coordinate.
    end : int
        End coordinate.
    ax : axis
        Axis to plot on.
    gtf_file : str
        Path to GTF file.
    """
    
    a = pandas.read_csv(gtf_file, sep = "\t", header = None)
    a = a[(a[0] == chrm) & (a[3] <= end) & (a[4] >= start)]

    transcripts = {}
    for i, r in a.iterrows():
        if r[2] == 'transcript':
            gene = r[8].split(";")[0][9:-1]
            if gene[:3] == 'MIR': continue # ignore microRNA
            if r[6] == '+':
                  ax.add_patch(patches.Rectangle((r[3], 0.4), r[4] - r[3] + 1, 0.3, color = 'skyblue'))
            else:
                  ax.add_patch(patches.Rectangle((r[3], -0.7), r[4] - r[3] + 1, 0.3, color = 'lightcoral'))
            if gene not in transcripts:
                transcripts[gene] = (r[3], r[4], r[6])
            else:
                transcripts[gene] = (min(r[3], transcripts[gene][0]), max(r[4], transcripts[gene][1]), r[6])
        elif r[2] == 'exon': 
            gene = r[8].split(";")[0][9:-1] # ignore microRNA
            if gene[:3] == 'MIR': continue
            if r[6] == '+':
                  ax.add_patch(patches.Rectangle((r[3], 0.1), r[4] - r[3] + 1, 0.9, color = 'skyblue'))
            else:
                  ax.add_patch(patches.Rectangle((r[3], -1), r[4] - r[3] + 1, 0.9, color = 'lightcoral'))
        
    for t in transcripts:
        if transcripts[t][2] == '+':
            ax.text(transcripts[t][0] + 10, 1.2, '$\it{'+t+'}$')
        else:
            ax.text(transcripts[t][0] + 10, -1.6, '$\it{'+t+'}$')

    ax.set_xlim((start, end))
    ax.set_ylim((-1.9, 1.9))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False) # new
    ax.spines['right'].set_visible(False) # new
    ax.spines['left'].set_visible(False) # new
    ax.spines['bottom'].set_visible(False) # new

def get_fragment_counts(fragment_file, cell_info, chrm, start, end):
    """Not fully implemented.
    """
    tabixfile = pysam.TabixFile(fragment_file)
    arr = np.zeros(end - start).astype(np.uintc)
    for tsv in tabixfile.fetch(chrm, start, end):
        s = tsv.split()
        # get cell info
        if 'coassay_analysis#' + s[3] not in cell_info['cell_name'].values: continue
        arr[max(0, int(s[1]) - start) : int(s[2]) - start] += 1
    return arr

def plot_hist(hist, title):
    """Plot training loss and validation loss.
    """
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.legend(['loss', 'val_loss'])
    plt.xlabel('Epochs')
    plt.title(title)
    plt.show()
    plt.close()

def create_colormap(clusters):
    """Create color map for cell clusters.

    Parameters
    ----------
    clusters : [str]
        Cluster names.
    """
    stallion_cmap = ["#D51F26", "#272E6A", "#208A42", "#89288F", "#F47D2B", "#FEE500", "#8A9FD1", "#C06CAB", "#E6C2DC", "#90D5E4", "#89C75F", "#F37B7D", "#9983BD", "#D24B27", "#3BBCA8", "#6E4B9E", "#0C727C", "#7E1416", "#D8A767", "#3D3D3D"]
    n = len(clusters)
    if n <= 10:
        cmap = dict(zip(clusters, ['C' + str(i) for i in range(10)]))
        return cmap
    random.seed(10)
    random.shuffle(stallion_cmap)
    if n <= len(stallion_cmap):
        cmap = dict(zip(clusters, stallion_cmap))
        return cmap
    cmap = LinearSegmentedColormap.from_list("", stallion_cmap, N=n)
    cmap = [cmap(i) for i in range(n)]
    random.shuffle(cmap)
    cmap = dict(zip(clusters, cmap))
    return cmap

