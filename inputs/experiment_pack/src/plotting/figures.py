"""Plotting module: generate all manuscript-ready figures."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os


def set_style():
    """Set publication-quality matplotlib style."""
    plt.rcParams.update({
        'figure.figsize': (8, 6),
        'figure.dpi': 300,
        'font.size': 11,
        'font.family': 'sans-serif',
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'lines.linewidth': 1.5,
    })
    sns.set_palette("colorblind")


def plot_governance_frontier(pareto_objectives, sweet_mask=None, 
                              output_path='outputs/figures/fig1_frontier.png'):
    """Fig 1: Governance efficiency frontier (detection vs throughput)."""
    set_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel A: Detection vs Throughput
    ax = axes[0]
    if len(pareto_objectives) > 0:
        ax.scatter(pareto_objectives[:, 1], pareto_objectives[:, 0],
                   c=pareto_objectives[:, 2], cmap='RdYlGn_r', 
                   s=40, alpha=0.7, edgecolors='k', linewidth=0.3)
        if sweet_mask is not None and np.any(sweet_mask):
            sweet = pareto_objectives[sweet_mask]
            ax.scatter(sweet[:, 1], sweet[:, 0], 
                       marker='*', s=150, c='blue', zorder=5,
                       label='Sweet-spot region')
            ax.legend()
    
    ax.set_xlabel('Safe Throughput')
    ax.set_ylabel('Unsafe Detection Rate')
    ax.set_title('A: Governance Efficiency Frontier')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axhline(y=0.7, color='gray', linestyle='--', alpha=0.5, label='Min detection')
    ax.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='Min throughput')
    
    # Panel B: Harm vs Friction
    ax = axes[1]
    if len(pareto_objectives) > 0:
        sc = ax.scatter(pareto_objectives[:, 3], pareto_objectives[:, 2],
                        c=pareto_objectives[:, 0], cmap='RdYlGn',
                        s=40, alpha=0.7, edgecolors='k', linewidth=0.3)
        plt.colorbar(sc, ax=ax, label='Detection Rate')
    
    ax.set_xlabel('Total Friction Cost')
    ax.set_ylabel('False Negative Harm')
    ax.set_title('B: Harm-Friction Trade-off')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def plot_threshold_heatmaps(grid_results, output_path='outputs/figures/fig2_heatmap.png'):
    """Fig 2: Policy threshold heatmaps."""
    set_style()
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    metrics = ['unsafe_detection_rate', 'safe_throughput', 
               'false_negative_harm', 'mean_total_friction']
    titles = ['Unsafe Detection Rate', 'Safe Throughput',
              'False Negative Harm', 'Mean Friction']
    cmaps = ['RdYlGn', 'RdYlGn', 'RdYlGn_r', 'RdYlGn_r']
    
    for idx, (metric, title, cmap) in enumerate(zip(metrics, titles, cmaps)):
        ax = axes[idx // 2][idx % 2]
        if metric in grid_results:
            data = grid_results[metric]
            if isinstance(data, np.ndarray) and data.ndim == 2:
                im = ax.imshow(data, cmap=cmap, aspect='auto', origin='lower')
                plt.colorbar(im, ax=ax)
                ax.set_xlabel('Evidence Gate')
                ax.set_ylabel('Safety Gate')
            else:
                ax.text(0.5, 0.5, 'Insufficient data', transform=ax.transAxes,
                        ha='center', va='center')
        else:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes,
                    ha='center', va='center')
        ax.set_title(title)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def plot_sensitivity_ranking(sobol_results, output_path='outputs/figures/fig3_sensitivity.png'):
    """Fig 3: Sobol sensitivity ranking."""
    set_style()
    n_outputs = len(sobol_results)
    fig, axes = plt.subplots(1, min(n_outputs, 4), figsize=(16, 5))
    if n_outputs == 1:
        axes = [axes]
    
    for idx, (outcome, df) in enumerate(sobol_results.items()):
        if idx >= 4:
            break
        ax = axes[idx]
        if 'ST' in df.columns:
            df_sorted = df.sort_values('ST', ascending=True)
            colors = ['#e74c3c' if s == 'ASSUMED' else '#3498db' 
                       for s in df_sorted.get('status', ['configured'] * len(df_sorted))]
            ax.barh(range(len(df_sorted)), df_sorted['ST'].values, color=colors, alpha=0.8)
            ax.set_yticks(range(len(df_sorted)))
            ax.set_yticklabels(df_sorted['parameter'].values, fontsize=8)
            ax.set_xlabel('Total-order Sobol Index')
        ax.set_title(outcome.replace('_', ' ').title(), fontsize=10)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def plot_drift_dynamics(lifecycle_results, output_path='outputs/figures/fig4_drift.png'):
    """Fig 4: Drift dynamics over time."""
    set_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Panel A: Performance decay trajectories
    ax = axes[0]
    decay_ts = lifecycle_results.get('performance_decay_ts', np.zeros((100, 12)))
    n_show = min(50, decay_ts.shape[0])
    for i in range(n_show):
        ax.plot(decay_ts[i, :], alpha=0.1, color='steelblue')
    ax.plot(np.mean(decay_ts, axis=0), color='darkblue', linewidth=2, label='Mean')
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Performance Decay')
    ax.set_title('A: Decay Trajectories')
    ax.legend()
    
    # Panel B: Harm over time
    ax = axes[1]
    harm_ts = lifecycle_results.get('harm_ts', np.zeros((100, 12)))
    ax.plot(np.mean(harm_ts, axis=0), color='red', linewidth=2, label='Mean')
    ax.fill_between(range(harm_ts.shape[1]),
                    np.percentile(harm_ts, 25, axis=0),
                    np.percentile(harm_ts, 75, axis=0),
                    alpha=0.3, color='red')
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Realised Harm')
    ax.set_title('B: Harm Over Time')
    ax.legend()
    
    # Panel C: Re-audit triggers
    ax = axes[2]
    reaudit = lifecycle_results.get('re_audit_triggered', np.zeros((100, 12)))
    reaudit_rate = np.mean(reaudit, axis=0)
    ax.bar(range(len(reaudit_rate)), reaudit_rate, color='orange', alpha=0.7)
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Re-audit Trigger Rate')
    ax.set_title('C: Re-audit Triggers')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def plot_decision_curve(dca_results, output_path='outputs/figures/fig5_dca.png'):
    """Fig 5: Decision Curve Analysis."""
    set_style()
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    
    thresholds = dca_results.get('thresholds', np.linspace(0.01, 0.99, 50))
    
    for policy_name, net_benefits in dca_results.get('policies', {}).items():
        ax.plot(thresholds[:len(net_benefits)], net_benefits, label=policy_name, linewidth=2)
    
    # Reference lines
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.plot(thresholds, np.zeros_like(thresholds), 'k--', alpha=0.5, label='Treat none')
    
    ax.set_xlabel('Threshold Probability')
    ax.set_ylabel('Net Benefit')
    ax.set_title('Decision Curve Analysis')
    ax.legend(loc='best')
    
    # Shade policy-relevant region
    ax.axvspan(0.05, 0.50, alpha=0.1, color='blue', label='Policy-relevant range')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def plot_scm_diagram(output_path='outputs/figures/fig6_scm.png'):
    """Fig 6: SCM diagram."""
    set_style()
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Create a visual representation of the SCM
    import networkx as nx
    
    G = nx.DiGraph()
    edges = [
        ('intrinsic_safety', 'baseline_harm'),
        ('clinical_utility', 'baseline_benefit'),
        ('bias_harm_index', 'subgroup_mult.'),
        ('subgroup_mult.', 'realised_harm'),
        ('uncertainty_cal.', 'abstention_rate'),
        ('abstention_rate', 'escalation_wkld'),
        ('fallback_safety', 'fallback_harm'),
        ('evidence_str.', 'audit_signal_q.'),
        ('evidence_vis.', 'audit_signal_q.'),
        ('traceability', 'audit_signal_q.'),
        ('audit_signal_q.', 'gate_scores'),
        ('gate_scores', 'audit_verdict'),
        ('stress_robust.', 'stress_failure'),
        ('stress_failure', 'realised_harm'),
        ('drift_suscept.', 'perf_decay'),
        ('data_shift_rate', 'perf_decay'),
        ('perf_decay', 'harm_over_time'),
        ('perf_decay', 're_audit_trigger'),
        ('adv_gaming', 'misreporting'),
        ('misreporting', 'observed_signals'),
    ]
    G.add_edges_from(edges)
    
    pos = nx.spring_layout(G, seed=42, k=2.5)
    
    # Color nodes by type
    latent = {'intrinsic_safety', 'clinical_utility', 'uncertainty_cal.',
              'bias_harm_index', 'fallback_safety', 'evidence_str.',
              'evidence_vis.', 'traceability', 'stress_robust.',
              'drift_suscept.', 'data_shift_rate', 'adv_gaming'}
    intermediate = {'baseline_harm', 'baseline_benefit', 'subgroup_mult.',
                    'abstention_rate', 'audit_signal_q.', 'stress_failure',
                    'perf_decay', 'misreporting'}
    outcomes = {'realised_harm', 'escalation_wkld', 'fallback_harm',
                'gate_scores', 'audit_verdict', 'harm_over_time',
                're_audit_trigger', 'observed_signals'}
    
    colors = []
    for node in G.nodes():
        if node in latent:
            colors.append('#3498db')
        elif node in intermediate:
            colors.append('#f39c12')
        else:
            colors.append('#e74c3c')
    
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors,
            node_size=1800, font_size=7, font_weight='bold',
            arrowsize=15, edge_color='gray', width=1.5,
            connectionstyle='arc3,rad=0.1')
    
    ax.set_title('Structural Causal Model (SCM)', fontsize=14, fontweight='bold')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#3498db', label='Latent traits'),
        Patch(facecolor='#f39c12', label='Intermediate'),
        Patch(facecolor='#e74c3c', label='Outcomes'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path


def generate_all_figures(sim_results, output_dir='outputs/figures'):
    """Generate all manuscript figures."""
    os.makedirs(output_dir, exist_ok=True)
    figures = {}
    
    figures['fig1'] = plot_governance_frontier(
        sim_results.get('pareto_objectives', np.zeros((10, 4))),
        sim_results.get('sweet_mask', None),
        os.path.join(output_dir, 'fig1_frontier.png'))
    
    figures['fig2'] = plot_threshold_heatmaps(
        sim_results.get('grid_results', {}),
        os.path.join(output_dir, 'fig2_heatmap.png'))
    
    figures['fig3'] = plot_sensitivity_ranking(
        sim_results.get('sobol_results', {}),
        os.path.join(output_dir, 'fig3_sensitivity.png'))
    
    figures['fig4'] = plot_drift_dynamics(
        sim_results.get('lifecycle_results', {}),
        os.path.join(output_dir, 'fig4_drift.png'))
    
    figures['fig5'] = plot_decision_curve(
        sim_results.get('dca_results', {}),
        os.path.join(output_dir, 'fig5_dca.png'))
    
    figures['fig6'] = plot_scm_diagram(
        os.path.join(output_dir, 'fig6_scm.png'))
    
    return figures
