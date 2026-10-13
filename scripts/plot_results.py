"""Original research graphics; plotted values are independent diagnostics only."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
(ROOT / 'figures').mkdir(exist_ok=True)
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.dpi': 120, 'savefig.dpi': 180, 'pdf.fonttype': 42})
def data(name):
    return np.genfromtxt(str(ROOT / 'results' / name), delimiter=',', names=True)
def save(fig, name):
    fig.savefig(str(ROOT / 'figures' / (name + '.pdf')), bbox_inches='tight',
                metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(str(ROOT / 'figures' / (name + '.png')), bbox_inches='tight')
    plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.4), constrained_layout=True)
e = data('emissions_curve.csv')
ax[0].plot(e['years_after_peak'], e['annual_recurrence'], label='Printed annual recurrence')
ax[0].plot(e['years_after_peak'], e['continuous_logistic'], '--', label='Continuous logistic limit')
ax[0].set(xlabel='Years after manufactured peak', ylabel='Emissions / peak emissions',
          title='(a) Decline rate 0.07 per year')
ax[0].legend(fontsize=8)
e = data('emissions_limit.csv')
for gamma in np.unique(e['decline_per_year']):
    sub = e[e['decline_per_year'] == gamma]
    ax[1].plot(sub['step_years'], 100*sub['remaining_fraction'], 'o-', label=str(gamma) + ' per year')
ax[1].set(xlabel='Diagnostic time step (years)', ylabel='Residual emissions (% of peak)',
          title='(b) Residual after 2000 years')
ax[1].legend(fontsize=8)
save(fig, 'diagnostic_emissions')

fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.4), constrained_layout=True)
g = data('greenland_convergence.csv')
ax[0].loglog(g['step_years'], g['absolute_error_m'], 'o-', label='RK4 error')
ax[0].loglog(g['step_years'], g['absolute_error_m'][-1]*(g['step_years']/g['step_years'][-1])**4,
             '--', label='Fourth-order slope')
ax[0].set(xlabel='Time step (years)', ylabel='Volume error (m sea-level equivalent)', title='(a) Greenland relaxation')
ax[0].legend(fontsize=8)
d = data('diffusion_convergence.csv')
ax[1].loglog(d['cells'], d['max_error_k'], 'o-', label='Column error')
ax[1].loglog(d['cells'], d['max_error_k'][0]*(d['cells'][0]/d['cells'])**2, '--', label='Second-order slope')
ax[1].set(xlabel='Number of depth cells', ylabel='Maximum temperature error (K)', title='(b) Ocean diffusion eigenmode')
ax[1].legend(fontsize=8)
save(fig, 'diagnostic_convergence')

fig, ax = plt.subplots(1, 3, figsize=(11, 3.1), constrained_layout=True)
d = data('flood_damage.csv')
ax[0].plot(d['water_height_m'], d['damage_usd']/1e6)
ax[0].set(xlabel='Water height (m)', ylabel='Event loss (million USD)', title='(a) Manufactured segment')
d = data('flood_reference_comparison.csv')
ax[1].loglog(d['panels'], np.maximum(d['absolute_difference_usd_per_year'], 1e-12), 'o-')
ax[1].set(xlabel='Simpson panels', ylabel='Difference from SciPy (USD/year)', title='(b) Expected-loss convergence')
d = data('protection_sensitivity.csv')
ax[2].plot(d['crest_m'], d['expected_loss_usd_per_year']/1e3)
ax[2].set(xlabel='Protection crest (m)', ylabel='Expected loss (thousand USD/year)', title='(c) Overtopping threshold')
save(fig, 'diagnostic_flood')

fig, ax = plt.subplots(figsize=(6, 3.3), constrained_layout=True)
d = data('anto_transform.csv')
ax.plot(d['temperature_c'], d['ocean_temperature_c'], label='B17 Eq. 6, literal expression')
ax.axhline(-1.8, color='black', ls='--', label='Stated freezing floor')
ax.set(xlabel='Manufactured global temperature input (degree C)',
       ylabel='Antarctic ocean temperature (degree C)')
ax.legend(fontsize=8)
save(fig, 'diagnostic_anto')

# Figure4 is conceptual: these boxes explicitly show incomplete implementation.
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.set(xlim=(0, 10), ylim=(0, 7)); ax.axis('off')
boxes = [
    (0.2, 5.2, 4.1, 1.1, 'Emissions + carbon + climate',
     'Implemented: coupled climate, carbon alternative,\nobservational climate calibration and checks', '#d8e9f3'),
    (5.5, 5.2, 4.1, 1.1, 'Sea-level components',
     'Implemented: GIC/GIS response, heat expansion,\ngeometric DAIS and event-aware integration', '#d8e9f3'),
    (5.5, 3.1, 4.1, 1.1, 'Coastal sea level and flood exposure',
     'Implemented: fingerprint operator,\nGEV extremes, elevation-band damage', '#d8e9f3'),
    (0.2, 3.1, 4.1, 1.1, 'Coastal costs and adaptation',
     'Implemented: annual synthetic cash flows,\nretained strategy, discounting and summaries', '#d8e9f3'),
    (0.2, 0.5, 9.4, 1.4, 'Remaining requirements for the target climate-to-cost ensemble',
     'Target joint emissions/climate/ice calibration and initialization; component fingerprints;\nland motion; original elevation-area and exposure data; matched socioeconomic inputs.\nIndependent alternatives are tested separately and are not target numerical reproductions.', '#f3e5d8')]
for x, y, w, h, title, desc, color in boxes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06',facecolor=color,edgecolor='#52606d'))
    ax.text(x+w/2,y+h-.22,title,ha='center',va='center',weight='bold',fontsize=10)
    ax.text(x+w/2,y+h/2-.18,desc,ha='center',va='center',fontsize=9)
for xy, start, label, tx, ty in [((5.45,5.75),(4.35,5.75),'T, ocean heat',4.9,6.25),
                               ((7.55,4.28),(7.55,5.12),'Component sea level',8.7,4.7),
                               ((4.35,3.65),(5.45,3.65),'Local sea level',4.9,4.55)]:
    ax.annotate('',xy=xy,xytext=start,arrowprops={'arrowstyle':'->','lw':1.5})
    ax.text(tx,ty,label,ha='center',fontsize=8)
ax.text(5,6.7,'Independent reconstruction: conceptual workflow (target Figure 4)',ha='center',fontsize=12)
save(fig, 'figure4_workflow')
print('Generated Figure4 schematic and four diagnostic figures (PDF and PNG).')
