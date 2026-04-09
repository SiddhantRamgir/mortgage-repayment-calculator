import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Mortgage Repayment Calculator", layout="wide")

st.title("Mortgage Repayment Calculator")

st.write("### Input Data")
col1, col2 = st.columns(2)

home_value = col1.number_input("Home Value ($)", min_value=0.0, value=500000.0)
deposit = col1.number_input("Deposit ($)", min_value=0.0, value=100000.0)
interest_rate = col2.number_input("Interest Rate (%)", min_value=0.0, value=8.5)
loan_term = col2.number_input("Loan Term (years)", min_value=1, value=30)

if deposit > home_value:
    st.error("Deposit cannot be greater than home value.")
    st.stop()

loan_amount = home_value - deposit
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = int(loan_term * 12)

# Standard monthly repayment formula
if monthly_interest_rate == 0:
    monthly_payment = loan_amount / number_of_payments
else:
    monthly_payment = (
        loan_amount
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
        / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    )

st.write("### Missed Payment Options")

missed_months = st.multiselect(
    "Select the month(s) where payment was missed",
    options=list(range(1, number_of_payments + 1)),
    help="If a month is selected, no payment will be made in that month. Interest still gets added."
)

# Summary metrics
total_scheduled_payment = monthly_payment * number_of_payments

m1, m2, m3 = st.columns(3)
m1.metric("Loan Amount", f"${loan_amount:,.2f}")
m2.metric("Standard Monthly Payment", f"${monthly_payment:,.2f}")
m3.metric("Loan Term", f"{loan_term} years")

# Build amortization schedule
schedule = []
remaining_balance = loan_amount

for month in range(1, number_of_payments + 1):
    opening_balance = remaining_balance
    interest_payment = opening_balance * monthly_interest_rate

    if month in missed_months:
        actual_payment = 0.0
        principal_payment = 0.0
        closing_balance = opening_balance + interest_payment
        payment_status = "Missed"
    else:
        actual_payment = monthly_payment
        principal_payment = actual_payment - interest_payment

        # Prevent overpayment on final month
        if principal_payment > opening_balance:
            principal_payment = opening_balance
            actual_payment = principal_payment + interest_payment

        closing_balance = opening_balance - principal_payment
        payment_status = "Paid"

    closing_balance = max(0, closing_balance)
    year = math.ceil(month / 12)

    schedule.append({
        "Month": month,
        "Year": year,
        "Opening Balance": opening_balance,
        "Interest Payment": interest_payment,
        "Principal Payment": principal_payment,
        "Actual Payment": actual_payment,
        "Closing Balance": closing_balance,
        "Status": payment_status
    })

    remaining_balance = closing_balance

df = pd.DataFrame(schedule)

total_paid = df["Actual Payment"].sum()
total_interest_paid = df["Interest Payment"].sum()
remaining_loan = df["Closing Balance"].iloc[-1]

st.write("### Results")
r1, r2, r3 = st.columns(3)
r1.metric("Total Paid", f"${total_paid:,.2f}")
r2.metric("Total Interest Charged", f"${total_interest_paid:,.2f}")
r3.metric("Remaining Balance After Term", f"${remaining_loan:,.2f}")

if remaining_loan > 0:
    st.warning(
        "Because some payments were missed, the loan is not fully repaid by the end of the original term."
    )

st.write("### Monthly Amortization Schedule")
st.dataframe(df, use_container_width=True)

# -----------------------------
# LINE GRAPH: Loan balance over time
# -----------------------------
st.write("### Line Graph: Loan Balance Decreasing Over Time")

fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df["Month"], df["Closing Balance"], marker="o", linewidth=1.5)
ax1.set_xlabel("Month")
ax1.set_ylabel("Remaining Loan Balance ($)")
ax1.set_title("Remaining Loan Balance by Month")
ax1.grid(True)

# Mark missed payment months
if missed_months:
    missed_df = df[df["Month"].isin(missed_months)]
    ax1.scatter(
        missed_df["Month"],
        missed_df["Closing Balance"],
        s=80,
        label="Missed Payment Month"
    )
    ax1.legend()

st.pyplot(fig1)

# -----------------------------
# BAR GRAPH: Principal vs Interest by month
# -----------------------------
st.write("### Bar Graph: Principal vs Interest Payment by Month")

fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.bar(df["Month"], df["Principal Payment"], label="Principal Payment")
ax2.bar(
    df["Month"],
    df["Interest Payment"],
    bottom=df["Principal Payment"],
    label="Interest Payment"
)
ax2.set_xlabel("Month")
ax2.set_ylabel("Amount ($)")
ax2.set_title("Monthly Payment Breakdown")
ax2.legend()

st.pyplot(fig2)

# -----------------------------
# EXTRA BAR GRAPH: Actual payment vs missed months
# -----------------------------
st.write("### Bar Graph: Actual Payments by Month")

fig3, ax3 = plt.subplots(figsize=(12, 5))
bars = ax3.bar(df["Month"], df["Actual Payment"])
ax3.set_xlabel("Month")
ax3.set_ylabel("Actual Payment ($)")
ax3.set_title("Actual Payment Made Each Month")

st.pyplot(fig3)

# -----------------------------
# YEARLY SUMMARY
# -----------------------------
st.write("### Yearly Summary")

yearly_summary = df.groupby("Year").agg({
    "Actual Payment": "sum",
    "Principal Payment": "sum",
    "Interest Payment": "sum",
    "Closing Balance": "last"
}).reset_index()

yearly_summary.columns = [
    "Year",
    "Total Payment",
    "Total Principal Paid",
    "Total Interest Paid",
    "Ending Balance"
]

st.dataframe(yearly_summary, use_container_width=True)