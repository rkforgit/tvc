import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("TVC vs Non-TVC Dashboard")

# Sidebar inputs
st.sidebar.header("Investment Parameters")
expected_return = st.sidebar.slider("Expected Annual Return Before Fee (%)", 0.0, 15.0, 7.0) / 100
fee_tvc = st.sidebar.number_input("TVC Annual Fee (%)", value=0.8) / 100
tax_saving_percent = st.sidebar.number_input("Tax Saving on TVC (%)", value=17) / 100
current_age = st.sidebar.number_input("Current Age", value=25)

base_investment = 60000
fee_non_tvc = 0
retirement_age = 65
expected_return_tvc = expected_return
expected_return_non_tvc = expected_return

# Age range
start_ages = np.arange(current_age, retirement_age)

# Growth from current age
years_to_retirement = retirement_age - current_age
initial_tvc = base_investment
initial_non_tvc = base_investment * (1 - tax_saving_percent)

tvc_growth = [initial_tvc]
non_tvc_growth = [initial_non_tvc]

for year in range(1, years_to_retirement + 1):
    tvc_growth.append(tvc_growth[-1] * (1 + expected_return_tvc - fee_tvc))
    non_tvc_growth.append(non_tvc_growth[-1] * (1 + expected_return_non_tvc - fee_non_tvc))

growth_ages = np.arange(current_age, retirement_age + 1)

# --- Plot fund growth from current age ---
fig_growth = go.Figure()

fig_growth.add_trace(go.Scatter(x=growth_ages, y=tvc_growth,
                                mode='lines+markers', name='TVC Growth', line=dict(color='blue'), hovertemplate='TVC: Age %{x} = $%{y:,.0f}<extra></extra>'))
fig_growth.add_trace(go.Scatter(x=growth_ages, y=non_tvc_growth,
                                mode='lines+markers', name='Non-TVC Growth', line=dict(color='orange'), hovertemplate='Non-TVC: Age %{x} = $%{y:,.0f}<extra></extra>'))

# Add invisible trace for difference
diff_values = np.array(tvc_growth) - np.array(non_tvc_growth)
fig_growth.add_trace(go.Scatter(
    x=growth_ages,
    y=diff_values,
    mode='markers',
    name='Difference',
    marker=dict(opacity=0),  # invisible
    hovertemplate='Age %{x}<br>TVC = $%{customdata[0]:,.0f}<br>'
                  'Non-TVC = $%{customdata[1]:,.0f}<br>'
                  'Difference = $%{customdata[2]:,.0f}<extra></extra>',
    customdata=np.stack([tvc_growth, non_tvc_growth, diff_values], axis=-1)
))

# Annotate difference at retirement
x = retirement_age
y1 = non_tvc_growth[-1]
y2 = tvc_growth[-1]
mid_y = (y1 + y2) / 2
diff = y2 - y1

# Choose color: green if positive, red if negative
diff_color = "green" if diff >= 0 else "red"

fig_growth.add_shape(type="line",
                     x0=x, y0=y1, x1=x, y1=y2,
                     line=dict(color=diff_color, width=2),
                     xref="x", yref="y")

fig_growth.add_annotation(x=x+5, y=mid_y,
                          text=f"${diff:,.0f}",
                          showarrow=False,
                          font=dict(size=20, color=diff_color))

fig_growth.update_layout(title="Fund Growth from Current Age to Retirement",
                         xaxis_title="Age",
                         yaxis_title="Fund Value",
                         template="plotly_white")

st.plotly_chart(fig_growth, use_container_width=True)

# --- Calculations for breakeven dashboard ---
tvc_final = []
non_tvc_final = []
difference = []

for start_age in start_ages:
    years = retirement_age - start_age
    initial_tvc = base_investment
    initial_non_tvc = base_investment * (1 - tax_saving_percent)

    tvc_value = initial_tvc * ((1 + expected_return_tvc - fee_tvc) ** years)
    non_tvc_value = initial_non_tvc * ((1 + expected_return_non_tvc - fee_non_tvc) ** years)

    tvc_final.append(tvc_value)
    non_tvc_final.append(non_tvc_value)
    difference.append(tvc_value - non_tvc_value)

# Breakeven age
breakeven_index = next((i for i, diff in enumerate(difference) if diff >= 0), None)
breakeven_age = start_ages[breakeven_index] if breakeven_index is not None else None

# --- Plotting breakeven dashboard ---
fig_breakeven = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              row_heights=[0.4, 0.6],
                              subplot_titles=("Portfolio Value vs Initial Investment Age",
                                              "Difference in Final Value (TVC - Non-TVC)"))

# Top plot
fig_breakeven.add_trace(go.Scatter(x=start_ages, y=tvc_final,
                                   mode='lines+markers', name='TVC Final Value', line=dict(color='blue'), hovertemplate='Age %{x} = $%{y:,.0f}<extra></extra>'),
                        row=1, col=1)
fig_breakeven.add_trace(go.Scatter(x=start_ages, y=non_tvc_final,
                                   mode='lines+markers', name='Non-TVC Final Value', line=dict(color='orange'), hovertemplate='Age %{x} = $%{y:,.0f}<extra></extra>'),
                        row=1, col=1)

if breakeven_age is not None:
    fig_breakeven.add_vline(x=breakeven_age, line=dict(color="gray", dash="dash"), row=1, col=1)
    fig_breakeven.add_annotation(x=breakeven_age+0.5, y=max(tvc_final)*0.8,
                                 text=f"Breakeven at age {breakeven_age}",
                                 showarrow=False, row=1, col=1,
                                 font=dict(size=18, color="red"))

# Bottom plot
colors = ['green' if d >= 0 else 'red' for d in difference]
fig_breakeven.add_trace(go.Bar(x=start_ages, y=difference, marker_color=colors, name="Difference", hovertemplate='Age %{x} = $%{y:,.0f}<extra></extra>'),
                        row=2, col=1)

max_diff = max(abs(d) for d in difference)
fig_breakeven.update_yaxes(range=[-max_diff*1.2, max_diff*1.2], row=2, col=1)

fig_breakeven.update_layout(height=700, template="plotly_white",
                            xaxis_title="Initial Investment Age",
                            yaxis_title="Portfolio Value at Age 65")

st.plotly_chart(fig_breakeven, use_container_width=True)

