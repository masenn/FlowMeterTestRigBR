import pandas as pd
import matplotlib.pyplot as plt

NORMALIZED_SUFFIX = '_N'

def normalize(data):
    return data - min(data)

def mod_dataset(df):
    df['t'] = normalize(df['SYS'])
    df['DELTA'] = df['UP'] - df['DOWN']
    df[f'UP{NORMALIZED_SUFFIX}'] = normalize(df['UP'])
    df[f'DOWN{NORMALIZED_SUFFIX}'] = normalize(df['DOWN'])
    df[f'AMB{NORMALIZED_SUFFIX}'] = normalize(df['AMB'])
    df[f'DELTA{NORMALIZED_SUFFIX}'] = normalize(df['DELTA'])
    return df

def load_dataset(file_name, test_directory='./tests/'):
    df = pd.read_csv(f'{test_directory}{file_name}')
    df['t'] = normalize(df['SYS'])
    df['DELTA'] = df['UP'] - df['DOWN']
    df[f'UP{NORMALIZED_SUFFIX}'] = normalize(df['UP'])
    df[f'DOWN{NORMALIZED_SUFFIX}'] = normalize(df['DOWN'])
    df[f'AMB{NORMALIZED_SUFFIX}'] = normalize(df['AMB'])
    df[f'DELTA{NORMALIZED_SUFFIX}'] = normalize(df['DELTA'])
    return df

def graph_dataset_timebased(df,normalize=True):
    fig, axes = plt.subplots(2, 2, figsize=(10,8))

    ax_up, ax_down, ax_amb, ax_flow = axes.flatten()

    # Upstream Voltage
    ax_up.set_xlabel('Time')
    ax_up.set_ylabel(f'{'Normalized ' if normalize else ''}Upstream Voltage (V)')
    ax_up.set_title(f'{'Normalized ' if normalize else ''}Upstream Voltage vs. Time (s)')
    ax_up.scatter(df['t'],df[f'UP{'_N' if normalize else ''}'])
    # Downstream Voltage
    ax_down.set_xlabel('Time')
    ax_down.set_ylabel(f'{'Normalized ' if normalize else ''}Downstream Voltage (V)')
    ax_down.set_title(f'{'Normalized ' if normalize else ''}Downstream Voltage vs. Time (s)')
    ax_down.scatter(df['t'],df[f'DOWN{'_N' if normalize else ''}'])
    # Ambient Normalized Voltage
    ax_amb.set_xlabel('Time')
    ax_amb.set_ylabel(f'{'Normalized ' if normalize else ''}Ambient Voltage (V)')
    ax_amb.set_title(f'{'Normalized ' if normalize else ''}Ambient Voltage vs. Time (s)')
    ax_amb.scatter(df['t'],df[f'AMB{'_N' if normalize else ''}'])

    # Flow
    window_size = 10
    ax_flow.set_xlabel('Flow (ccm)')
    ax_flow.set_ylabel('Delta (V)')
    ax_flow.set_title(f'{'Normalized ' if normalize else ''}Delta vs. Time (s)')
    ax_flow.scatter(df['FLOW'],df[f'DELTA{'_N' if normalize else ''}'])

    plt.tight_layout()

def fuck_off():
    print('fuck off')
    pass

def scatter_multiple(xs,ys,xlabel,ylabel,normalize=True):
    fig, axes = plt.subplots(len(xs),1, figsize=(10,5*len(xs)))
    for i,ax in enumerate(axes.flatten()):
        # Flow
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'{ylabel} vs. {xlabel}')
        ax.scatter(xs[i],ys[i])
    plt.tight_layout()
