import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

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

# Plot fund growth from current age
fig_growth, ax = plt.subplots(figsize=(12, 5))
ax.plot(growth_ages, tvc_growth, label='TVC Growth', color='blue')
ax.plot(growth_ages, non_tvc_growth, label='Non-TVC Growth', color='orange')
ax.set_xlabel('Age')
ax.set_ylabel('Fund Value')
ax.set_title('Fund Growth from Current Age to Retirement')
ax.legend()
ax.grid(True)

# Annotate difference at age 65 with vertical double-arrow line
x = retirement_age
y1 = non_tvc_growth[-1]
y2 = tvc_growth[-1]
mid_y = (y1 + y2) / 2
diff = y2 - y1

# Draw vertical line with arrowheads
ax.annotate('', xy=(x, y1), xytext=(x, y2),
            arrowprops=dict(arrowstyle='<->', color='red', linewidth=2))

# Display value at center
ax.text(x + 0.5, mid_y, f'${diff:,.0f}', va='center', ha='left', fontsize=20, color='red')

st.pyplot(fig_growth)

# Calculations for breakeven dashboard
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

# Plotting breakeven dashboard
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# Top plot: Portfolio values
ax1.plot(start_ages, tvc_final, label='TVC Final Value', color='blue')
ax1.plot(start_ages, non_tvc_final, label='Non-TVC Final Value', color='orange')
ax1.set_ylabel('Portfolio Value at Age 65')
ax1.legend(loc='upper right')
ax1.grid(True)
ax1.set_title('Portfolio Value vs Initial Investment Age')

# Annotate breakeven
if breakeven_age is not None:
    ax1.axvline(breakeven_age, color='gray', linestyle='--')
    ax1.text(breakeven_age + 0.5, max(tvc_final) * 0.8,
             f'Breakeven at age {breakeven_age}', color='black')

# Bottom plot: Difference
colors = ['green' if d >= 0 else 'red' for d in difference]
ax2.bar(start_ages, difference, color=colors, alpha=0.6)
ax2.set_ylabel('TVC - Non-TVC Difference')
ax2.set_xlabel('Initial Investment Age')
ax2.grid(True)
ax2.set_title('Difference in Final Value (TVC - Non-TVC)')

# Auto-scale Y-axis
max_diff = max(abs(d) for d in difference)
ax2.set_ylim(-max_diff * 1.2, max_diff * 1.2)

st.pyplot(fig)
