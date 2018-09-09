# J. Dirani
# Quick way to plot eelbrain results

import mne, eelbrain
import numpy as np


def plot(res, ds, out_dir, match, subjects_dir, surf=None):

    '''
    Plot Timecourse, Brain, and Barplot of signidicant clusters from an eelbrain ANOVA/t-test results object.


    Parameters
    -------------
    res : eelbrain ANOVA or t-test result object

    ds: eelbrain.Dataset
    Dataset containing stcs and condidion labels needs to be specified

    out_dir : str
    Output directory, ends with "/"

    surf : 'inflated' | 'pial' | 'smoothwm' | 'sphere' | 'white'
    surfer.Brain surface to use as brain geometry. Default = 'white'

    match : str | None
    Match cases for a repeated measures design in pairwsie t-test for barplots.


    subjects_dir : str
    subjects directory associated with the source space dimension.

    '''


    if surf == None:
        surf = 'white'

    src = ds['stc']

    mask_sign_clusters = np.where(res.clusters['p'] <= 0.05, True, False)
    sign_clusters = res.clusters[mask_sign_clusters]

    for i in range(sign_clusters.n_cases):
        cluster_nb = i+1
        cluster = sign_clusters[i]['cluster']
        tstart = sign_clusters[i]['tstart']
        tstop = sign_clusters[i]['tstop']
        effect = sign_clusters[i]['effect']

        effect = effect.replace(' x ', '%') # Changing format of string for interaction effects.

        # save significant cluster as a temporary label for plotting.
        ds['stc'] = src
        label = eelbrain.labels_from_clusters(cluster)
        label[0].name = 'TempLabel-lh'
        mne.write_labels_to_annot(label,subject='fsaverage', parc='workspace' ,subjects_dir=subjects_dir, overwrite=True)
        src.source.set_parc('workspace')
        src_region = src.sub(source='TempLabel-lh')
        ds['stc'] = src_region
        timecourse = src_region.mean('source')


        #Plot
            # 1)Timecourse
        activation = eelbrain.plot.UTSStat(timecourse, effect, ds=ds, title = 'Effect = %s, cluster #%s'%(effect, cluster_nb))
        activation.add_vspan(xmin=tstart, xmax=tstop, color='lightgrey', zorder=-50)
        activation.save(out_dir+'Cluster #%s, Effect = %s - Timecourse.png'%(cluster_nb, effect))
        activation.close()
            # 2) Brain
        brain = eelbrain.plot.brain.cluster(cluster.mean('time'), subjects_dir=subjects_dir, surf=surf, colorbar=True)
        brain.save_image(out_dir+'Cluster #%s, Effect = %s - Brain.png'%(cluster_nb, effect))
        brain.close()
            # 3) Bars
        ds['average_source_activation'] = timecourse.mean(time=(tstart,tstop))
        bar = eelbrain.plot.Barplot(ds['average_source_activation'], X=effect, ds=ds, match=match)
        bar.save(out_dir+'Cluster #%s, Effect = %s - Bars.png'%(cluster_nb, effect))
        bar.close()


    ds['stc'] = src # resets ds['stc'] before exiting the loop. Otherwise, returns an errror if make_report is run again.
